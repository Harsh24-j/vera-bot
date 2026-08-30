#!/usr/bin/env python3
"""
Vera Bot Backend — Merchant AI Assistant for WhatsApp

A deterministic, trigger-aware composer that generates contextual messages
for merchants across 5 service categories (dentists, salons, restaurants, gyms, pharmacies).

Implements all 5 required endpoints:
  - GET /v1/healthz
  - GET /v1/metadata
  - POST /v1/context
  - POST /v1/tick
  - POST /v1/reply
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
import json
import hashlib
import re
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, List, Any, Literal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CategoryContext:
    slug: str
    display_name: str
    voice: dict
    offer_catalog: list
    peer_stats: dict
    digest: list
    patient_content_library: list = field(default_factory=list)
    seasonal_beats: list = field(default_factory=list)
    trend_signals: list = field(default_factory=list)


@dataclass
class MerchantContext:
    merchant_id: str
    category_slug: str
    identity: dict
    subscription: dict
    performance: dict
    offers: list
    conversation_history: list
    customer_aggregate: dict
    signals: list = field(default_factory=list)
    review_themes: list = field(default_factory=list)


@dataclass
class CustomerContext:
    customer_id: str
    merchant_id: str
    identity: dict
    relationship: dict
    state: str
    preferences: dict
    consent: dict


@dataclass
class TriggerContext:
    id: str
    scope: str
    kind: str
    source: str
    merchant_id: str
    customer_id: Optional[str]
    payload: dict
    urgency: int
    suppression_key: str
    expires_at: str


# ============================================================================
# GLOBAL BOT STATE
# ============================================================================

class BotState:
    """Maintains all contexts and conversation state."""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.categories: Dict[str, dict] = {}  # slug -> full category context
        self.merchants: Dict[str, dict] = {}  # merchant_id -> merchant context + version
        self.customers: Dict[str, dict] = {}  # customer_id -> customer context + version
        self.triggers: Dict[str, dict] = {}  # trigger_id -> trigger context + version
        self.conversations: Dict[str, dict] = {}  # conversation_id -> state
        self.suppressed_keys: set = set()  # suppression keys (de-dup)
        self.ended_conversations: set = set()  # ended conversation IDs
    
    def get_context_counts(self):
        return {
            "category": len(self.categories),
            "merchant": len(self.merchants),
            "customer": len(self.customers),
            "trigger": len(self.triggers),
        }
    
    def get_uptime_seconds(self):
        return int((datetime.now(timezone.utc) - self.start_time).total_seconds())
    
    def accept_category(self, context_id: str, version: int, payload: dict) -> tuple:
        """Accept/reject category context based on versioning."""
        existing = self.categories.get(context_id)
        if existing and existing["version"] >= version:
            return False, {"accepted": False, "reason": "stale_version", "current_version": existing["version"]}
        
        now = datetime.now(timezone.utc).isoformat()
        self.categories[context_id] = {"version": version, "payload": payload, "delivered_at": now}
        ack_id = f"ack_{context_id}_v{version}"
        return True, {"accepted": True, "ack_id": ack_id, "stored_at": now}
    
    def accept_merchant(self, context_id: str, version: int, payload: dict) -> tuple:
        """Accept/reject merchant context based on versioning."""
        existing = self.merchants.get(context_id)
        if existing and existing["version"] >= version:
            return False, {"accepted": False, "reason": "stale_version", "current_version": existing["version"]}
        
        now = datetime.now(timezone.utc).isoformat()
        self.merchants[context_id] = {"version": version, "payload": payload, "delivered_at": now}
        ack_id = f"ack_{context_id}_v{version}"
        return True, {"accepted": True, "ack_id": ack_id, "stored_at": now}
    
    def accept_customer(self, context_id: str, version: int, payload: dict) -> tuple:
        """Accept/reject customer context based on versioning."""
        existing = self.customers.get(context_id)
        if existing and existing["version"] >= version:
            return False, {"accepted": False, "reason": "stale_version", "current_version": existing["version"]}
        
        now = datetime.now(timezone.utc).isoformat()
        self.customers[context_id] = {"version": version, "payload": payload, "delivered_at": now}
        ack_id = f"ack_{context_id}_v{version}"
        return True, {"accepted": True, "ack_id": ack_id, "stored_at": now}
    
    def accept_trigger(self, context_id: str, version: int, payload: dict) -> tuple:
        """Accept/reject trigger context based on versioning."""
        existing = self.triggers.get(context_id)
        if existing and existing["version"] >= version:
            return False, {"accepted": False, "reason": "stale_version", "current_version": existing["version"]}
        
        now = datetime.now(timezone.utc).isoformat()
        self.triggers[context_id] = {"version": version, "payload": payload, "delivered_at": now}
        ack_id = f"ack_{context_id}_v{version}"
        return True, {"accepted": True, "ack_id": ack_id, "stored_at": now}


bot_state = BotState()


# ============================================================================
# COMPOSER ENGINE
# ============================================================================

class MessageComposer:
    """Composes messages from category, merchant, trigger, and optional customer contexts."""
    
    def __init__(self, bot_state: BotState):
        self.bot_state = bot_state
    
    def compose_message(self, merchant_id: str, trigger_id: str, customer_id: Optional[str] = None) -> Optional[dict]:
        """
        Compose a message for the given merchant/customer and trigger.
        Returns action dict or None if should not send.
        """
        # Load contexts
        trigger_data = self.bot_state.triggers.get(trigger_id)
        merchant_data = self.bot_state.merchants.get(merchant_id)
        
        if not trigger_data or not merchant_data:
            return None
        
        trigger = trigger_data["payload"]
        merchant = merchant_data["payload"]
        category_slug = merchant.get("category_slug")
        category_data = self.bot_state.categories.get(category_slug)
        
        if not category_data:
            return None
        
        category = category_data["payload"]
        
        # Check suppression
        if trigger.get("suppression_key") in self.bot_state.suppressed_keys:
            return None
        
        # Build conversation ID
        conversation_id = self._build_conversation_id(merchant_id, trigger_id, customer_id)
        
        # Skip if already ended
        if conversation_id in self.bot_state.ended_conversations:
            return None
        
        # Compose based on trigger kind
        trigger_kind = trigger.get("kind", "").lower()
        
        if trigger_kind == "research_digest":
            return self._compose_research_digest(
                conversation_id, merchant_id, customer_id, trigger_id,
                trigger, merchant, category
            )
        elif trigger_kind == "perf_spike":
            return self._compose_perf_spike(
                conversation_id, merchant_id, customer_id, trigger_id,
                trigger, merchant, category
            )
        elif trigger_kind == "recall_due":
            return self._compose_recall_due(
                conversation_id, merchant_id, customer_id, trigger_id,
                trigger, merchant, category
            )
        elif trigger_kind == "dormant_with_vera":
            return self._compose_dormant_reengagement(
                conversation_id, merchant_id, customer_id, trigger_id,
                trigger, merchant, category
            )
        else:
            # Generic trigger handler
            return self._compose_generic(
                conversation_id, merchant_id, customer_id, trigger_id,
                trigger, merchant, category
            )
    
    def _build_conversation_id(self, merchant_id: str, trigger_id: str, customer_id: Optional[str]) -> str:
        """Build a unique conversation ID."""
        parts = [merchant_id, trigger_id.split("_")[1] if "_" in trigger_id else trigger_id]
        if customer_id:
            parts.append(customer_id.split("_")[1])
        conv_hash = hashlib.md5("_".join(parts).encode()).hexdigest()[:8]
        return f"conv_{merchant_id}_{conv_hash}"
    
    def _compose_research_digest(self, conv_id: str, merchant_id: str, customer_id: Optional[str],
                                  trigger_id: str, trigger: dict, merchant: dict, category: dict) -> dict:
        """Compose a research digest message."""
        merchant_name = merchant["identity"].get("owner_first_name", "there")
        category_slug = merchant["category_slug"]
        
        # Find top digest item
        digest_items = category.get("digest", [])
        top_item_id = trigger.get("payload", {}).get("top_item_id")
        top_item = next((d for d in digest_items if d.get("id") == top_item_id), digest_items[0] if digest_items else None)
        
        if not top_item:
            return None
        
        # Build message
        subject = top_item.get("title", "Research update")
        source = top_item.get("source", "Industry source")
        
        # Find merchant signals that align
        merchant_signals = merchant.get("signals", [])
        matching_signal = None
        if "high_risk_adult" in " ".join(merchant_signals):
            matching_signal = "high-risk adult cohort"
        
        # Compose body
        if matching_signal:
            body = (f"Dr. {merchant_name}, {category_slug.rstrip('s')} research digest just landed. "
                   f"One item relevant to your {matching_signal} — {subject}. "
                   f"Worth a look (2-min read)? Want me to pull the summary + draft a patient reminder?")
        else:
            body = (f"Dr. {merchant_name}, just got the latest research digest for {category_slug}. "
                   f"Thought you'd find this one useful: {subject}. "
                   f"Interested in the details?")
        
        body += f" — {source}"
        
        return {
            "conversation_id": conv_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": "vera",
            "trigger_id": trigger_id,
            "template_name": "vera_research_digest_v1",
            "template_params": [merchant_name, subject, source],
            "body": body,
            "cta": "open_ended",
            "suppression_key": trigger.get("suppression_key", ""),
            "rationale": f"External research digest with {category_slug} anchor. Source-cited for credibility. Open-ended CTA invites engagement without pressure.",
        }
    
    def _compose_perf_spike(self, conv_id: str, merchant_id: str, customer_id: Optional[str],
                            trigger_id: str, trigger: dict, merchant: dict, category: dict) -> dict:
        """Compose a performance spike notification."""
        merchant_name = merchant["identity"].get("owner_first_name", "there")
        perf = merchant.get("performance", {})
        delta_7d = perf.get("delta_7d", {})
        views_delta = delta_7d.get("views_pct", 0) * 100
        
        if views_delta > 0:
            body = (f"Dr. {merchant_name}, your profile views jumped {views_delta:.0f}% this week! "
                   f"That's {perf.get('views', 0)} views in the last 30 days. "
                   f"Good momentum. Want to capitalize with a fresh offer or post?")
        else:
            body = f"Dr. {merchant_name}, heads up — your profile activity is down. Let's figure out why together."
        
        return {
            "conversation_id": conv_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": "vera",
            "trigger_id": trigger_id,
            "template_name": "vera_perf_spike_v1",
            "body": body,
            "cta": "open_ended",
            "suppression_key": trigger.get("suppression_key", ""),
            "rationale": "Actionable performance insight with clear next steps.",
        }
    
    def _compose_recall_due(self, conv_id: str, merchant_id: str, customer_id: Optional[str],
                            trigger_id: str, trigger: dict, merchant: dict, category: dict) -> dict:
        """Compose a patient recall reminder."""
        merchant_name = merchant["identity"].get("owner_first_name", "there")
        category_slug = merchant["category_slug"]
        
        body = (f"Dr. {merchant_name}, one of your patients (ID: {customer_id[:8] if customer_id else 'N/A'}) "
               f"is due for their {category_slug.rstrip('s')} checkup. "
               f"Want me to draft a WhatsApp reminder you can send?")
        
        return {
            "conversation_id": conv_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": "vera",
            "trigger_id": trigger_id,
            "template_name": "vera_recall_v1",
            "body": body,
            "cta": "binary_yes_no",
            "suppression_key": trigger.get("suppression_key", ""),
            "rationale": "Patient-specific, time-sensitive reminder with clear call-to-action.",
        }
    
    def _compose_dormant_reengagement(self, conv_id: str, merchant_id: str, customer_id: Optional[str],
                                      trigger_id: str, trigger: dict, merchant: dict, category: dict) -> dict:
        """Compose a re-engagement message for dormant merchants."""
        merchant_name = merchant["identity"].get("owner_first_name", "there")
        category_slug = merchant["category_slug"]
        
        # Check subscription status
        sub_status = merchant.get("subscription", {}).get("status", "unknown")
        
        body = f"Dr. {merchant_name}, haven't heard from you in a while. How's the {category_slug} practice going? Anything I can help with?"
        
        if sub_status == "expired":
            body += f" (Also, your subscription lapsed — want to renew?)"
        
        return {
            "conversation_id": conv_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": "vera",
            "trigger_id": trigger_id,
            "template_name": "vera_reengagement_v1",
            "body": body,
            "cta": "open_ended",
            "suppression_key": trigger.get("suppression_key", ""),
            "rationale": "Low-friction re-engagement check-in without being pushy.",
        }
    
    def _compose_generic(self, conv_id: str, merchant_id: str, customer_id: Optional[str],
                        trigger_id: str, trigger: dict, merchant: dict, category: dict) -> dict:
        """Generic fallback composer."""
        merchant_name = merchant["identity"].get("owner_first_name", "there")
        trigger_kind = trigger.get("kind", "update")
        
        body = f"Hi {merchant_name}, got an update for you about {trigger_kind}. Interested in details?"
        
        return {
            "conversation_id": conv_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": "vera",
            "trigger_id": trigger_id,
            "template_name": "vera_generic_v1",
            "body": body,
            "cta": "open_ended",
            "suppression_key": trigger.get("suppression_key", ""),
            "rationale": "Generic trigger handler.",
        }


composer = MessageComposer(bot_state)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route("/v1/healthz", methods=["GET"])
def healthz():
    """Health check with context count."""
    return jsonify({
        "status": "ok",
        "uptime_seconds": bot_state.get_uptime_seconds(),
        "contexts_loaded": bot_state.get_context_counts(),
    }), 200


@app.route("/v1/metadata", methods=["GET"])
def metadata():
    """Bot metadata and team info."""
    return jsonify({
        "team_name": "Vera Bot Challenge Team",
        "team_members": ["Bot Builder"],
        "model": "claude-3-5-sonnet-20241022",
        "approach": "Multi-context composer with trigger-kind dispatch, suppression dedup, and conversation state management",
        "contact_email": "bot@magicpin.ai",
        "version": "1.0.0",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }), 200


@app.route("/v1/context", methods=["POST"])
def receive_context():
    """Receive and store context (category, merchant, customer, or trigger)."""
    try:
        payload = request.get_json(force=True, silent=False)
        if not payload:
            return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    scope = payload.get("scope")
    context_id = payload.get("context_id")
    version = payload.get("version", 1)
    context_payload = payload.get("payload", {})
    
    accepted = False
    response = {}
    
    try:
        if scope == "category":
            accepted, response = bot_state.accept_category(context_id, version, context_payload)
        elif scope == "merchant":
            accepted, response = bot_state.accept_merchant(context_id, version, context_payload)
        elif scope == "customer":
            accepted, response = bot_state.accept_customer(context_id, version, context_payload)
        elif scope == "trigger":
            accepted, response = bot_state.accept_trigger(context_id, version, context_payload)
        else:
            return jsonify({"error": f"Unknown scope: {scope}"}), 400
        
        status_code = 200 if accepted else 409
        return jsonify(response), status_code
    
    except Exception as e:
        logger.error(f"Error receiving context: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/v1/tick", methods=["POST"])
def tick():
    """Decide which messages to send based on available triggers."""
    try:
        payload = request.get_json(force=True, silent=False)
        if not payload:
            return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    now = payload.get("now", datetime.now(timezone.utc).isoformat())
    available_triggers = payload.get("available_triggers", [])
    
    actions = []
    
    try:
        for trigger_id in available_triggers:
            trigger_data = bot_state.triggers.get(trigger_id)
            if not trigger_data:
                continue
            
            trigger = trigger_data["payload"]
            merchant_id = trigger.get("merchant_id")
            customer_id = trigger.get("customer_id")
            
            # Check if trigger has expired
            expires_at = trigger.get("expires_at")
            if expires_at and expires_at < now:
                continue
            
            # Check suppression
            suppression_key = trigger.get("suppression_key")
            if suppression_key and suppression_key in bot_state.suppressed_keys:
                continue
            
            # Compose message
            action = composer.compose_message(merchant_id, trigger_id, customer_id)
            if action:
                actions.append(action)
                # Mark suppression key to prevent duplicate sends
                if suppression_key:
                    bot_state.suppressed_keys.add(suppression_key)
        
        return jsonify({"actions": actions}), 200
    
    except Exception as e:
        logger.error(f"Error in tick: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/v1/reply", methods=["POST"])
def reply():
    """Handle merchant/customer replies and decide follow-up actions."""
    try:
        payload = request.get_json(force=True, silent=False)
        if not payload:
            return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    conversation_id = payload.get("conversation_id")
    merchant_id = payload.get("merchant_id")
    customer_id = payload.get("customer_id")
    message = payload.get("message", "").lower()
    from_role = payload.get("from_role", "merchant")
    turn_number = payload.get("turn_number", 1)
    
    try:
        # Check if conversation is ended
        if conversation_id in bot_state.ended_conversations:
            return jsonify({"action": "end", "rationale": "Conversation already ended."}), 200
        
        # Detect auto-reply patterns
        if _is_auto_reply(message):
            wait_seconds = 14400  # 4 hours
            return jsonify({
                "action": "wait",
                "wait_seconds": wait_seconds,
                "rationale": "Detected WhatsApp Business auto-reply. Backing off 4 hours to wait for merchant owner.",
            }), 200
        
        # Detect hard opt-out
        if _is_hard_optout(message):
            bot_state.ended_conversations.add(conversation_id)
            return jsonify({
                "action": "end",
                "rationale": "Merchant explicitly opted out. Closing conversation.",
            }), 200
        
        # Detect affirmative responses
        if _is_affirmative(message):
            follow_up = _generate_follow_up(merchant_id, customer_id, "affirmative")
            if follow_up:
                return jsonify(follow_up), 200
        
        # Detect out-of-scope requests
        if _is_out_of_scope(message):
            return jsonify({
                "action": "send",
                "body": "I'll have to leave that to your specialists — that's outside what I can help with directly. Let me know if there's anything else I can assist with!",
                "cta": "open_ended",
                "rationale": "Out-of-scope request politely declined; offer to refocus conversation.",
            }), 200
        
        # Detect questions/curiosity
        if "?" in message or _is_question(message):
            follow_up = _generate_follow_up(merchant_id, customer_id, "question")
            if follow_up:
                return jsonify(follow_up), 200
        
        # Default: send a supportive follow-up
        return jsonify({
            "action": "send",
            "body": "Got it. How can I help you move forward with that?",
            "cta": "open_ended",
            "rationale": "Default engaged response to keep conversation flowing.",
        }), 200
    
    except Exception as e:
        logger.error(f"Error in reply: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# REPLY HELPERS
# ============================================================================

def _is_auto_reply(message: str) -> bool:
    """Detect WhatsApp Business auto-reply patterns."""
    patterns = [
        r"thank you for contacting",
        r"our team will respond",
        r"we appreciate your message",
        r"auto-reply",
        r"automated response",
    ]
    msg_lower = message.lower()
    return any(re.search(pattern, msg_lower) for pattern in patterns)


def _is_hard_optout(message: str) -> bool:
    """Detect explicit opt-out."""
    patterns = [
        r"stop messaging",
        r"unsubscribe",
        r"not interested",
        r"don't message",
        r"leave me alone",
        r"stop sending",
    ]
    msg_lower = message.lower()
    return any(re.search(pattern, msg_lower) for pattern in patterns)


def _is_affirmative(message: str) -> bool:
    """Detect affirmative responses."""
    patterns = [r"\byes?\b", r"\bsure\b", r"\bplease\b", r"\bgo ahead\b", r"\bsend\b"]
    msg_lower = message.lower()
    return any(re.search(pattern, msg_lower) for pattern in patterns)


def _is_question(message: str) -> bool:
    """Detect if message is a question."""
    return "?" in message or message.strip().endswith("?")


def _is_out_of_scope(message: str) -> bool:
    """Detect out-of-scope requests."""
    patterns = [
        r"gst",
        r"tax",
        r"legal",
        r"accounting",
        r"investment",
        r"medical advice",
    ]
    msg_lower = message.lower()
    return any(re.search(pattern, msg_lower) for pattern in patterns)


def _generate_follow_up(merchant_id: str, customer_id: Optional[str], interaction_type: str) -> Optional[dict]:
    """Generate a contextual follow-up message."""
    merchant_data = bot_state.merchants.get(merchant_id)
    if not merchant_data:
        return None
    
    merchant = merchant_data["payload"]
    merchant_name = merchant["identity"].get("owner_first_name", "there")
    offers = merchant.get("offers", [])
    
    if interaction_type == "affirmative" and offers:
        active_offer = next((o for o in offers if o.get("status") == "active"), None)
        if active_offer:
            return {
                "action": "send",
                "body": f"Great! I'm sending over the details. In the meantime, have you promoted your {active_offer.get('title', 'current offer')} yet?",
                "cta": "open_ended",
                "rationale": "Affirmed engagement — follow up with contextual question.",
            }
    
    return {
        "action": "send",
        "body": f"Understood, {merchant_name}. Let me know what works best for you.",
        "cta": "open_ended",
        "rationale": "Supportive follow-up to maintain engagement.",
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Vera Bot server...")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
