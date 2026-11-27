# Security Policy: PII Pseudonymization & Simulation Sandbox Isolation

## Reporting a Vulnerability
Report vulnerabilities privately to **Favour Ikeoluwa Adamson** (`favouradamson803@gmail.com`).

## Core Sandbox Security Controls
1. **Zero-PII Log Ingestion:** All CloudTrail, Azure Activity, and GCP Audit logs pass through keyed HMAC-SHA256 pseudonymization prior to sandbox replay.
2. **Read-Only Replay Isolation:** The simulation sandbox holds zero write credentials to production cloud accounts.
3. **SOX 404 / FedRAMP CM-3 WORM Proofs:** Every pre-enforcement simulation digest is anchored in tri-cloud Object Lock storage.
