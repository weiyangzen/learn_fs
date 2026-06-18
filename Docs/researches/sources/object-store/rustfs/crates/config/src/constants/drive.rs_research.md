<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/drive.rs -->
# sources/object-store/rustfs/crates/config/src/constants/drive.rs

## Purpose
Centralizes environment names and defaults for drive operation timeouts, active health probes, recovery thresholds, timeout-to-health policy, and timeout profile presets.

## Important APIs, types, and functions
Exports legacy `ENV_DRIVE_MAX_TIMEOUT_DURATION`, per-operation timeout keys for metadata, disk info, list-dir, walk-dir, and stall detection, plus active check interval/timeout keys. Health policy constants are `DRIVE_TIMEOUT_HEALTH_ACTION_MARK_FAILURE` and `DRIVE_TIMEOUT_HEALTH_ACTION_IGNORE_SCANNER`. Recovery tuning includes suspect failure, returning success, returning probe, offline grace, and long-offline thresholds. `RUSTFS_DRIVE_TIMEOUT_PROFILE=high_latency` maps to a 60-second preset.

## Control flow
No executable logic; downstream code reads these constants to choose timeouts and drive-state transitions.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with local/remote drive wrappers, scanner-sensitive walk/list paths, disk health state machines, and operator environment parsing.

## Risks and edge cases
Timeout defaults are short and can mark storage failed under high latency. The `ignore_scanner` policy changes health semantics for scanner workloads and must stay aligned with drive-state code. Legacy fallback plus per-operation overrides can create precedence ambiguity if parsers drift.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Drive-state tests should cover timeout classification, high-latency profile precedence, returning-drive thresholds, and scanner timeout policy.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/drive.rs -->
