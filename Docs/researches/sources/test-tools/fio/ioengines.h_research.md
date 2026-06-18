# sources/test-tools/fio/ioengines.h

## Purpose
Defines fio's I/O engine ABI: callback table, queue status values, engine flags, dynamic-engine entry type, and public wrapper declarations.

## Important APIs, Types, and Functions
`FIO_IOOPS_VERSION` is the ABI version. `enum fio_q_status` defines completed, queued, and busy queue outcomes. `struct ioengine_ops` includes lifecycle callbacks, queue/commit/event callbacks, file operations, memory hooks, `io_u` hooks, ZBD and FDP callbacks, engine-specific options, and dynamic-library handle storage. Flag enums define capabilities and constraints such as sync, raw, diskless, noextend, pipe, barrier, no stats, no offload, atomic writes, multi-range trim, and syncfs support. Public wrappers mirror the implementation in `ioengines.c`.

## Control Flow
Engines register or are dynamically loaded, then fio calls setup/init/post-init, per-I/O prep/queue/commit/getevents/event, file operations, and cleanup/free according to job lifecycle.

## State and Persistence Behavior
The header defines callback shape and capability flags only. Engine implementations own their private state through `td->io_ops_data`, `td->eo`, and `io_u->engine_data`.

## Dependencies and Integration Points
Includes compiler helpers, fio lists, `io_u.h`, ZBD types, and data placement types. Every ioengine implementation and core engine wrapper depends on this header.

## Risks
Any callback or flag changes require version coordination. Missing callbacks are only valid for sync engines or optional capabilities. Shared `ioengine_ops` structures can be mutated by core code and dynamic loading, so engines must respect fio's lifecycle.

## Test Signals
Build all configured engines, load dynamic engines, run `--enghelp`, and execute smoke jobs for sync, async, diskless, trim, syncfs, ZBD, and FDP-capable engines.
