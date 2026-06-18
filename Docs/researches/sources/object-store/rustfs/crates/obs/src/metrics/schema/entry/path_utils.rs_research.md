# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/path_utils.rs

## Purpose
Normalizes subsystem path strings into Prometheus metric-name segments.

## Important APIs, Types, and Functions
`format_path_to_metric_name(path: &str) -> String` trims leading `/` characters and replaces `/` and `-` with `_`.

## Control Flow
The function is a pure string transformation. `MetricSubsystem::as_str()` calls it for built-in and custom subsystem paths.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Used only by `subsystem.rs`. It controls the subsystem segment in `MetricDescriptor::get_full_metric_name()`.

## Risks
The normalization does not validate Prometheus identifier characters beyond slash and dash replacement. Spaces, dots, uppercase letters, or other punctuation in custom subsystem paths pass through unchanged.

## Test Signals
Tests cover leading slash trimming and slash/dash replacement for API, network, bucket, and cluster examples.
