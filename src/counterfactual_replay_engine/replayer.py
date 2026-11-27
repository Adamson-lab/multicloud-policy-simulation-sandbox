import argparse
import json
import os
import sys
from typing import List, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blast_radius_scorer.scorer import score_blast_radius_and_synthesize_exceptions
from merkle_simulation_ledger.verifier import seal_simulation_proof

HISTORICAL_30DAY_AUDIT_STREAM = [
    {"event_id": "evt-001", "cloud": "aws", "principal": "role/CorePaymentsLedger", "action": "kms:Decrypt", "region": "us-east-1", "baseline_verdict": "ALLOW"},
    {"event_id": "evt-002", "cloud": "aws", "principal": "role/SettlementBatchSync", "action": "s3:GetObject", "region": "us-east-1", "baseline_verdict": "ALLOW"},
    {"event_id": "evt-003", "cloud": "azure", "principal": "role/RetailMobileAPI", "action": "Microsoft.Storage/storageAccounts/read", "region": "eastus2", "baseline_verdict": "ALLOW"},
    {"event_id": "evt-004", "cloud": "gcp", "principal": "role/DevSandboxRunner", "action": "compute.instances.insert", "region": "ap-southeast-1", "baseline_verdict": "ALLOW"},
    {"event_id": "evt-005", "cloud": "aws", "principal": "role/DevSandboxRunner", "action": "ec2:RunInstances", "region": "ap-south-1", "baseline_verdict": "ALLOW"}
]

CANDIDATE_POLICIES = {
    "SCP-KMS-STRICT-01": {
        "description": "Deny kms:Decrypt across all roles unless invoked from VPC Endpoint vpce-9999",
        "deny_actions": ["kms:Decrypt"],
        "denied_regions": []
    },
    "SCP-BLOCK-UNAPPROVED-REGIONS-02": {
        "description": "Deny compute provisioning outside approved US/EU sovereign regions (us-east-1, eastus2, eu-central-1)",
        "deny_actions": [],
        "denied_regions": ["ap-southeast-1", "ap-south-1"]
    }
}

def run_counterfactual_replay(
    policy_id: str,
    events: List[Dict] = None,
    ledger_output: str = "evidence/merkle-receipts/latest_simulation_proof.json"
) -> Dict:
    stream = events if events is not None else HISTORICAL_30DAY_AUDIT_STREAM
    pol = CANDIDATE_POLICIES[policy_id]
    regressions = []

    for ev in stream:
        would_deny = (ev["action"] in pol["deny_actions"]) or (ev["region"] in pol["denied_regions"])
        candidate_verdict = "DENY" if would_deny else "ALLOW"
        if ev["baseline_verdict"] == "ALLOW" and candidate_verdict == "DENY":
            regressions.append({
                "event_id": ev["event_id"],
                "cloud": ev["cloud"],
                "principal": ev["principal"],
                "action": ev["action"],
                "region": ev["region"],
                "transition": "ALLOW -> DENY"
            })

    blast_summary = score_blast_radius_and_synthesize_exceptions(regressions)
    report = {
        "policy_id": policy_id,
        "policy_description": pol["description"],
        "events_replayed": len(stream),
        "regressions": regressions,
        "blast_summary": blast_summary,
        "proof_leaves": [
            {"policy_id": policy_id, "events_replayed": len(stream)},
            blast_summary
        ]
    }

    sealed = seal_simulation_proof(report)
    if ledger_output:
        os.makedirs(os.path.dirname(ledger_output), exist_ok=True)
        with open(ledger_output, "w", encoding="utf-8") as f:
            json.dump(sealed, f, indent=2)

    return sealed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Cloud Counterfactual Policy Simulation Replayer")
    parser.add_argument("--policy-id", default="SCP-BLOCK-UNAPPROVED-REGIONS-02")
    args = parser.parse_args()
    res = run_counterfactual_replay(args.policy_id)
    print(json.dumps(res["simulation_report"]["blast_summary"], indent=2))
    print("Merkle Root:", res["merkle_root_sha256"])
