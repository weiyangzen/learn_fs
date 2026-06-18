<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/scanner.rs -->
# sources/object-store/rustfs/crates/config/src/constants/scanner.rs

## Purpose
Defines scanner admin config keys, environment names/defaults, alert thresholds, concurrency budgets, idle/cache behavior, and the `ScannerSpeed` preset type.

## Important APIs, types, and functions
`SCANNER_KEYS` lists supported admin keys. Environment constants cover start delay, cycle, cycle object/directory/runtime budgets, speed, delay, max wait, bitrot cycle, alert thresholds, idle mode, cache save timeout, set/disk scan concurrency, yield frequency, and inline-heal compatibility. `ScannerSpeed` exposes `sleep_factor`, `max_sleep`, `cycle_interval`, `parse_str`, `from_env_str`, and `Display` for fastest/fast/default/slow/slowest.

## Control flow
Preset methods map variants to throttling and cycle durations. `parse_str` trims and lowercases input, returning `None` for unknown strings; `from_env_str` falls back to default. Display serializes the canonical lowercase name.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with data scanner scheduling, background bitrot scans, scanner cache persistence, alert generation for excessive versions/folders, heal-candidate enqueue, and admin config validation.

## Risks and edge cases
Scanner defaults can produce significant storage traversal load. `0` has special disable/unbounded semantics for multiple budgets. The deprecated start-delay alias must remain compatible while migration completes. Comments say inline heal is removed but the compatibility flag remains, so downstream behavior must only warn and continue enqueue-based healing.

## Test signals
Tests should cover all speed presets, parser fallback, display strings, budget zero semantics, deprecated alias precedence, cache save minimum, alert thresholds, and scanner/heal enqueue behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/scanner.rs -->
