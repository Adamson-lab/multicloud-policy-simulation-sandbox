import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from counterfactual_replay_engine.replayer import run_counterfactual_replay
from iac_plan_diff_simulator.plan_scanner import scan_iac_and_live_estate
from shadow_canary_promoter.promoter import evaluate_canary_promotion
from merkle_simulation_ledger.verifier import verify_simulation_ledger

class TestMultiCloudPolicySimulationSandbox(unittest.TestCase):
    def test_catastrophic_kms_policy_blocked_and_exception_synthesized(self):
        res = run_counterfactual_replay("SCP-KMS-STRICT-01", ledger_output=None)
        summary = res["simulation_report"]["blast_summary"]
        self.assertEqual(summary["gate_verdict"], "BLOCK_PR_HIGH_BLAST_RADIUS")
        self.assertEqual(len(summary["tier_0_critical_impacts"]), 1)
        self.assertEqual(summary["synthesized_least_privilege_exceptions"][0]["exempted_principal"], "role/CorePaymentsLedger")

    def test_safe_region_policy_approved_and_merkle_sealed(self):
        ledger_path = os.path.join(os.path.dirname(__file__), "../../evidence/merkle-receipts/latest_simulation_proof.json")
        res = run_counterfactual_replay("SCP-BLOCK-UNAPPROVED-REGIONS-02", ledger_output=ledger_path)
        summary = res["simulation_report"]["blast_summary"]
        self.assertEqual(summary["gate_verdict"], "APPROVE_FOR_SHADOW_CANARY")
        self.assertTrue(verify_simulation_ledger(ledger_path))

    def test_iac_plan_and_live_estate_whatif_scanner(self):
        scan = scan_iac_and_live_estate(require_cmk=True)
        self.assertIn("azure-sql-legacy-reporting", scan["existing_live_assets_flagged"])
        self.assertEqual(scan["recommended_rollout_mode"], "SHADOW_AUDIT_WITH_REMEDIATION_PR")

    def test_autonomous_circuit_breaker_reverts_on_access_denied_spike(self):
        decision = evaluate_canary_promotion(blast_score=10, shadow_days_observed=7, live_access_denied_per_min=520.0, baseline_denied_per_min=2.0)
        self.assertEqual(decision["stage"], "CIRCUIT_BREAKER_TRIPPED")

if __name__ == "__main__":
    unittest.main()
