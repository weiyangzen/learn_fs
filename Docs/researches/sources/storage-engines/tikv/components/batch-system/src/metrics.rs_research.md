# sources/storage-engines/tikv/components/batch-system/src/metrics.rs

## Purpose
Defines prometheus metrics for batch-system channels, scheduling, polling, and broadcast operations.

## APIs, Types, And Functions
`FsmType` has static labels `store` and `apply`. Auto-flush local metric vectors cover reschedule count, schedule wait duration, poll duration, poll rounds, and FSM count per poll. Global metrics include `CHANNEL_FULL_COUNTER_VEC`, histogram vectors for FSM timing/counting, and `BROADCAST_NORMAL_DURATION`.

## Control Flow
No direct control flow beyond lazy static registration. Runtime code in router and batch modules increments counters and observes histograms at send, schedule, poll, reschedule, and broadcast points.

## State And Persistence
Prometheus collectors store process-local metric state and export through the wider TiKV metrics subsystem. No source-level persistence exists.

## Dependencies And Integration Points
Uses `prometheus`, `prometheus_static_metric`, and `lazy_static`. `Fsm::FSM_TYPE` selects labels for each concrete FSM.

## Risks And Test Signals
Metric registration names are externally visible and should remain stable. Label cardinality is intentionally fixed by static enums. Runtime tests do not assert metric values, so regressions are mainly caught by compile-time label usage and production observability.
