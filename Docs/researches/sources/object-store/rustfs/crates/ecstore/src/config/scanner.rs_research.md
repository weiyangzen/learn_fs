# sources/object-store/rustfs/crates/ecstore/src/config/scanner.rs

## Purpose
This file defines scanner subsystem default KVS for object scanner pacing, cycle limits, bitrot cadence, cache save timeout, concurrency, yielding, and alert thresholds.

## Important APIs, types, and functions
`DEFAULT_KVS` is a `LazyLock<KVS>` containing scanner speed, delay, max wait, cycle, start delay, max duration/object/directory counts, bitrot cycle, idle mode, cache save timeout, max concurrent set/disk scans, yield frequency, and alert thresholds.

## Control flow
Only lazy initialization occurs. `config::init` registers these defaults under `SCANNER_SUB_SYS`; scanner runtime code elsewhere parses and applies the strings.

## State and persistence behavior
The file stores immutable defaults. Several optional timing fields use empty strings with `hidden_if_empty`, preserving a difference between absent override and explicit values.

## Dependencies and integration points
It depends on scanner constants from `rustfs_config` and `KV/KVS`. It integrates with server-config defaults, scanner scheduling, and data-usage cache/snapshot production indirectly.

## Risks and edge cases
Values are strings, so invalid changes are detected only downstream. Concurrency and cycle defaults affect background I/O load. Empty hidden fields must not be collapsed into zero values by consumers.

## Test signals
No local tests. `config/mod.rs` checks registration and representative speed/delay/max-wait/max-objects values, but not every key.
