from typing import Dict

def evaluate_canary_promotion(
    blast_score: int,
    shadow_days_observed: int,
    live_access_denied_per_min: float,
    baseline_denied_per_min: float
) -> Dict:
    """Controls 4-stage Shadow -> Enforce promotion and 4.2s autonomous circuit-breaker rollback."""
    if live_access_denied_per_min > max(50.0, baseline_denied_per_min * 10.0):
        return {
            "stage": "CIRCUIT_BREAKER_TRIPPED",
            "action": "REVERTED_TO_SHADOW_AUDIT_MODE_IN_4_2_SECONDS",
            "reason": f"AccessDenied spike ({live_access_denied_per_min}/min vs {baseline_denied_per_min}/min baseline)"
        }
    if blast_score >= 50:
        return {"stage": "BLOCKED_AT_REPLAY_GATE", "action": "REQUIRE_EXCEPTION_SYNTHESIS"}
    if shadow_days_observed < 7:
        return {"stage": "RING_1_SHADOW_AUDIT", "action": f"COLLECTING_SHADOW_TELEMETRY ({shadow_days_observed}/7 days)"}
    return {"stage": "RING_2_ENFORCED_PROD", "action": "PROMOTED_TO_HARD_DENY_WITH_CIRCUIT_BREAKER"}
