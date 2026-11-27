package enterprise.policy.simulation

default allow_promotion = false

allow_promotion if {
    input.simulation.events_replayed >= 1000
    input.blast_summary.blast_radius_score_0_to_100 < 50
    count(input.blast_summary.tier_0_critical_impacts) == 0
}
