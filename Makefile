.PHONY: demo test verify lint clean

demo:
	python3 src/counterfactual_replay_engine/replayer.py --policy-id SCP-KMS-STRICT-01
	python3 src/counterfactual_replay_engine/replayer.py --policy-id SCP-BLOCK-UNAPPROVED-REGIONS-02
	python3 src/iac_plan_diff_simulator/plan_scanner.py --require-cmk-encryption

test:
	python3 -m unittest discover -s tests -p "test_*.py" -v

verify:
	python3 src/merkle_simulation_ledger/verifier.py --ledger evidence/merkle-receipts/latest_simulation_proof.json

lint:
	python3 -m py_compile src/counterfactual_replay_engine/replayer.py src/blast_radius_scorer/scorer.py src/iac_plan_diff_simulator/plan_scanner.py src/shadow_canary_promoter/promoter.py src/merkle_simulation_ledger/verifier.py

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
