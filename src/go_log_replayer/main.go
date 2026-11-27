package main

import "fmt"

type AuditEvent struct {
	Principal string
	Action    string
	Region    string
}

func main() {
	events := []AuditEvent{
		{Principal: "role/CorePaymentsLedger", Action: "kms:Decrypt", Region: "us-east-1"},
		{Principal: "role/DevSandboxRunner", Action: "ec2:RunInstances", Region: "ap-south-1"},
	}
	regressions := 0
	for _, ev := range events {
		if ev.Region == "ap-south-1" {
			regressions++
		}
	}
	fmt.Printf("MPSS Go Log Replayer | Events Evaluated: %d | Candidate Regressions: %d\n", len(events), regressions)
}
