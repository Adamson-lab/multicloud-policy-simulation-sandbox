import argparse
import json
from typing import Dict

LIVE_AND_PLANNED_ASSETS = [
    {"asset_id": "aws-rds-core-payments", "source": "LIVE_ESTATE", "cmk_encrypted": True, "tls_min": "1.3"},
    {"asset_id": "azure-sql-legacy-reporting", "source": "LIVE_ESTATE", "cmk_encrypted": False, "tls_min": "1.2"},
    {"asset_id": "gcp-gcs-pr-412-staging", "source": "TERRAFORM_PLAN_PR_412", "cmk_encrypted": True, "tls_min": "1.3"}
]

def scan_iac_and_live_estate(require_cmk: bool = True) -> Dict:
    impacted_live = []
    blocked_prs = []
    for item in LIVE_AND_PLANNED_ASSETS:
        if require_cmk and not item["cmk_encrypted"]:
            if item["source"] == "LIVE_ESTATE":
                impacted_live.append(item["asset_id"])
            else:
                blocked_prs.append(item["asset_id"])

    return {
        "policy_check": "REQUIRE_CUSTOMER_MANAGED_KMS_ENCRYPTION",
        "total_assets_evaluated": len(LIVE_AND_PLANNED_ASSETS),
        "existing_live_assets_flagged": impacted_live,
        "in_flight_terraform_prs_blocked": blocked_prs,
        "recommended_rollout_mode": "SHADOW_AUDIT_WITH_REMEDIATION_PR" if impacted_live else "IMMEDIATE_ENFORCE"
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terraform Plan & Live Estate What-If Scanner")
    parser.add_argument("--require-cmk-encryption", action="store_true")
    args = parser.parse_args()
    print(json.dumps(scan_iac_and_live_estate(args.require_cmk_encryption), indent=2))
