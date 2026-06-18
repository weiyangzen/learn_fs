# sources/storage-engines/wiredtiger/src/support/timestamp.c Research

## Purpose
This support file centralizes timestamp and time-window string formatting plus validation of WiredTiger time metadata. It validates both per-value `WT_TIME_WINDOW` instances and page-level `WT_TIME_AGGREGATE` summaries, including their relationship to parent aggregates and the stable timestamp when parent aggregate information is absent.

## Important APIs, Types, and Functions
- `__wt_timestamp_to_string`, `__wt_time_point_to_string`, `__wt_time_window_to_string`, and `__wt_time_aggregate_to_string` format timestamp structures for diagnostics and error messages.
- `__wt_timestamp_to_hex_string` emits compact hexadecimal metadata form, with special handling for `WT_TS_NONE` and `WT_TS_MAX`.
- `__wt_verbose_timestamp` logs timestamp values under the timestamp verbose category.
- `__wt_time_aggregate_validate` checks page aggregate invariants and optionally checks containment within a parent aggregate.
- `__wt_time_value_validate` checks individual value time windows and optionally validates them against a parent aggregate.
- Static helpers `__time_aggregate_validate_parent_stable`, `__time_aggregate_validate_parent`, `__time_value_validate_parent_stable`, and `__time_value_validate_parent` implement the two parent modes.

## Control Flow and State
The formatting functions are leaf helpers: they write caller-owned buffers using WiredTiger snprintf utilities. Validation functions first enforce intrinsic ordering constraints, then decide whether parent validation is required. Metadata handles skip parent checks. If `parent == NULL` or the handle is metadata, validation succeeds after local checks. If a parent aggregate is empty, the child is checked against `__wt_get_stable_timestamp(session)` because an empty parent usually means there is no reliable aggregate data from older versions or downgrades. Otherwise the child time points must be contained by parent bounds.

## State and Persistence Behavior
The file does not mutate durable state. Its persistence impact is defensive: time windows and aggregates are embedded in pages, cells, history-store records, and metadata, and bad ordering can corrupt visibility or checkpoint behavior. It explicitly allows cases needed for timestampless truncates and upgrade/downgrade history, such as stop timestamps of `WT_TS_NONE` and empty parent aggregates treated as stable.

## Dependencies and Integration Points
The code depends on `WT_TIME_WINDOW`, `WT_TIME_AGGREGATE`, timestamp constants, transaction id constants, prepare flags, connection flag `WT_CONN_PRESERVE_PREPARED`, `WT_IS_METADATA`, and stable timestamp access. It is used by reconciliation, page validation, diagnostics, transaction/timestamp code, and tiered metadata formatting via `__wt_timestamp_to_hex_string`.

## Risks and Edge Cases
Validation is deliberately nuanced. A too-strict check can reject valid timestampless truncate or downgrade data; a too-loose check can permit impossible visibility intervals. Prepared updates are special: prepared start/stop windows must have prepare timestamps, and when preserve-prepared is active they must also have prepared ids; prepared windows must not simultaneously expose normal start/stop durable timestamps. Parent-empty checks use the current stable timestamp, so failures can be timing-sensitive. Error text depends on stack buffers, so callers must pass buffers sized by WiredTiger constants.

## Test Signals
Test cases should cover normal insert-only, all-deleted, and partially-deleted aggregate scenarios described in comments; timestampless truncate paths; parent containment failures; empty-parent stable timestamp failures; start/stop prepared windows with preserve-prepared both enabled and disabled; and metadata handles skipping parent checks. Negative tests should assert the exact class of `EINVAL` while silent mode returns `EINVAL` without emitting the formatted message.
