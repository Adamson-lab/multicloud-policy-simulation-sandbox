from typing import List, Dict

CMDB_SERVICE_CRITICALITY = {
    "role/CorePaymentsLedger": {"tier": "Tier-0", "weight": 100, "owner": "payments-sre@enterprise.io"},
    "role/SettlementBatchSync": {"tier": "Tier-0", "weight": 100, "owner": "settlement-ops@enterprise.io"},
    "role/RetailMobileAPI": {"tier": "Tier-1", "weight": 25, "owner": "digital-banking@enterprise.io"},
    "role/DevSandboxRunner": {"tier": "Tier-2", "weight": 1, "owner": "dev-platform@enterprise.io"}
}

def score_blast_radius_and_synthesize_exceptions(regressions: List[Dict]) -> Dict:
    """Computes CMDB-weighted Blast-Radius Score (0-100) and synthesizes narrow condition exceptions."""
    raw_weighted_score = 0
    tier0_impacts = []
    synthesized_exceptions = []

    for reg in regressions:
        principal = reg["principal"]
        meta = CMDB_SERVICE_CRITICALITY.get(principal, {"tier": "Tier-2", "weight": 1, "owner": "unmapped@enterprise.io"})
        raw_weighted_score += meta["weight"]
        if meta["tier"] == "Tier-0":
            tier0_impacts.append({
                "principal": principal,
                "action": reg["action"],
                "region": reg["region"],
                "owner": meta["owner"]
            })
            synthesized_exceptions.append({
                "condition_operator": "ArnNotLike",
                "condition_key": "aws:PrincipalArn",
                "exempted_principal": principal,
                "scoped_action": reg["action"],
                "rationale": f"Prevent Tier-0 outage on {principal} while enforcing guardrail for remaining 99.9% estate"
            })

    normalized_score = min(100, raw_weighted_score)
    gate_verdict = "BLOCK_PR_HIGH_BLAST_RADIUS" if (normalized_score >= 50 or len(tier0_impacts) > 0) else "APPROVE_FOR_SHADOW_CANARY"

    return {
        "blast_radius_score_0_to_100": normalized_score,
        "total_regressions_detected": len(regressions),
        "tier_0_critical_impacts": tier0_impacts,
        "gate_verdict": gate_verdict,
        "synthesized_least_privilege_exceptions": synthesized_exceptions
    }
