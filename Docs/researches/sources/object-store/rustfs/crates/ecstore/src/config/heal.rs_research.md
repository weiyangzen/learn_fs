# sources/object-store/rustfs/crates/ecstore/src/config/heal.rs

## Purpose
This file defines the heal subsystem's default configuration and a small runtime config holder for bitrot/heal scanning. It is mainly registered by `config/mod.rs` under `HEAL_SUB_SYS`.

## Important APIs, types, and functions
`DEFAULT_KVS` contains `HEAL_BITROT_CYCLE` with `DEFAULT_HEAL_BITROT_CYCLE_SECS`. `Config` stores `bitrot`, `sleep`, `io_count`, `drive_workers`, and `cache`, with `bitrot_scan_cycle`, `get_workers`, and `update`. `parse_bitrot_config` accepts boolean strings or month-suffixed values.

## Control flow
Default registration is passive. The parser first tries `parse_bool`; enabled maps to zero duration, disabled attempts a negative duration, and non-boolean values must end with `m` and be at least one month.

## State and persistence behavior
No direct persistence exists here. The default KVS is persisted only when the broader server-config system saves config. Runtime `Config` is plain in-memory state, and `update` does not copy `cache`.

## Dependencies and integration points
It depends on heal constants from `rustfs_config`, `KV/KVS`, `parse_bool`, and ecstore errors. `config/mod.rs` imports it for default registration.

## Risks and edge cases
`Duration::from_secs_f64(-1.0)` will panic if disabled parsing is reached. Month conversion uses `months * 30 * 24 * 60`, which appears to compute minutes rather than seconds. The parser is private and untested, and `update` leaving `cache` unchanged may make `bitrot_scan_cycle` stale.

## Test signals
There are no local tests. `config/mod.rs` only checks that the default heal bitrot-cycle KVS is registered.
