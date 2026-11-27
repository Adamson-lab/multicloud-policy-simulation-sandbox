import argparse
import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict

def sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def build_merkle_root(leaves: List[Dict]) -> str:
    if not leaves:
        return sha256_hex("EMPTY_SIMULATION_LEDGER")
    layer = [sha256_hex(json.dumps(item, sort_keys=True)) for item in leaves]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [sha256_hex(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]

def seal_simulation_proof(report: Dict) -> Dict:
    leaves = report.get("proof_leaves", [])
    root = build_merkle_root(leaves)
    return {
        "schema_version": "1.0.0-MPSS-SOX404-FEDRAMP-CM3",
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "merkle_root_sha256": root,
        "worm_storage_anchors": [
            f"s3://adamson-lab-sim-worm/proofs/{root[:16]}.json",
            f"https://adamsonlabsimworm.blob.core.windows.net/proofs/{root[:16]}.json",
            f"gs://adamson-lab-sim-worm-gcp/proofs/{root[:16]}.json"
        ],
        "simulation_report": report
    }

def verify_simulation_ledger(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    expected = doc["merkle_root_sha256"]
    recomputed = build_merkle_root(doc["simulation_report"]["proof_leaves"])
    if expected != recomputed:
        raise ValueError(f"SOX 404 SIMULATION TAMPER ALERT: {expected} != {recomputed}")
    print(f"[VERIFIED] Policy Simulation Merkle Root: {recomputed}")
    print(f"[VERIFIED] Policy ID: {doc['simulation_report']['policy_id']} | Verdict: {doc['simulation_report']['blast_summary']['gate_verdict']}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify SOX 404 & FedRAMP CM-3 Policy Simulation Proof")
    parser.add_argument("--ledger", required=True)
    args = parser.parse_args()
    verify_simulation_ledger(args.ledger)
