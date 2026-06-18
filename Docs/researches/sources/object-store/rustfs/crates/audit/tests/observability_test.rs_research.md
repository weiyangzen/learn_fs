# sources/object-store/rustfs/crates/audit/tests/observability_test.rs

## Purpose
This file validates the audit observability API: event counters, target success/failure counters, EPS calculation, latency and error-rate reporting, global metric wrappers, reset behavior, and human-readable formatting for metric and performance reports.

## Important APIs, Types, and Functions
Tests use `rustfs_audit::observability::*`, including `AuditMetrics`, `AuditMetricsReport`, `PerformanceValidation`, global `record_*` functions, `get_metrics_report`, and `reset_metrics`. Important methods include `record_event_success`, `record_event_failure`, `record_target_success`, `record_target_failure`, `generate_report`, `get_target_success_rate`, `validate_performance_requirements`, `get_events_per_second`, `get_error_rate`, `reset`, `format`, and `all_requirements_met`.

## Control Flow
Most tests instantiate `AuditMetrics`, record synthetic successes/failures with `Duration` values, and assert derived report fields. Performance validation compares average latency against a 30 ms requirement and error rate against a 1% threshold. EPS tests record 100 events, sleep briefly, then require a positive/high EPS. Formatting tests check expected numeric formatting and pass/fail symbols in rendered strings.

## State and Persistence Behavior
`AuditMetrics::new` is local to each test. Global metric functions mutate process-global observability state and are reset in the test. There is no persistence beyond in-memory counters and timestamps.

## Dependencies and Integration Points
The observability layer is used by `AuditSystem::start`, `reload_config`, `get_metrics`, `validate_performance`, and `reset_metrics`. These tests define expected metric semantics for system-level reporting and performance gates.

## Risks and Edge Cases
Global metrics can leak across tests unless reset. EPS tests depend on wall-clock timing and can be sensitive to overloaded CI. Exact floating point equality is asserted for some simple ratios, so implementation changes to rounding could break tests. The formatted strings include Unicode pass/fail symbols, which callers parsing output should treat as presentation, not stable machine API.

## Test Signals
Signals include zero initial metrics, success/failure counts, error rate `(failures / all events) * 100`, latency averaged across successes and failures, default target success rate of 100% when no operations exist, reset clearing all counters, and performance validation producing recommendations on failed requirements.
