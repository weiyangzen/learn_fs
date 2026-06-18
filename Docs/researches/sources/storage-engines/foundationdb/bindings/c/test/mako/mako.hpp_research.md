# sources/storage-engines/foundationdb/bindings/c/test/mako/mako.hpp

## Purpose
`mako.hpp` is the central public configuration header for the Mako benchmark. It defines benchmark modes, CLI option ids, operation ids, workload specification storage, default limits, and the `Arguments` structure shared by parser, worker, and reporting code.

## Important APIs, Types, and Functions
- `MODE_INVALID`, `MODE_CLEAN`, `MODE_BUILD`, `MODE_RUN`, and `MODE_REPORT` define executable behavior.
- `ArgKind` maps long-only command-line options to `getopt_long` values.
- `OpKind` defines operation ids used as indexes in `WorkloadSpec`, `opTable`, and statistics arrays.
- `WorkloadSpec::ops[MAX_OP][3]` stores per-operation count, range, and reverse flags.
- `Arguments` contains all run configuration: FDB API version, concurrency, mode, row/key/value sizing, TPS controls, transaction spec, cluster/database arrays, tracing/TLS/auth fields, JSON/export paths, timeout settings, and GRV queue delay.
- `setTransactionOptionsIfEnabled` applies transaction timeout and max GRV queue delay to an `fdb::Transaction`.

## Control Flow
The header is included by parser, workload, operations, and stats code. `Arguments` is initialized once in the main process, then copied through forked children where it is treated as immutable. `parseArguments` fills fields, `Arguments::validate` enforces cross-field invariants, `Arguments::setGlobalOptions` applies network-level FDB settings before network setup, and worker paths use the values to partition work and build transactions.

## State and Persistence Behavior
The header owns no runtime storage directly, but it defines fixed-size buffers that become process-local state after parsing. The most persistent effect is indirect: fields such as `json_output_path`, `stats_export_path`, `tracepath`, `cluster_files`, and report file arrays control external file or cluster interactions.

## Dependencies and Integration Points
It includes the FDB C++ wrapper `fdb_api.hpp`, POSIX/PThread types, and `limit.hpp` for path sizes. The operation ids are a hard contract with `operations.cpp`, `stats.hpp`, and report formatting.

## Risks
Many fields are plain `int` or fixed char arrays, so parser and validation code must maintain bounds. `MAX_OP` must remain last because arrays and loops depend on it. Adding an operation requires updating this enum, `operations.cpp`, parser strings, stats/report logic, and tests together.

## Test Signals
The best validation is building all Mako translation units and running parser smoke tests across modes, operation specs, timeout options, TLS paths, tracing, and report export. Operation additions should be caught by tests that confirm `MAX_OP`-indexed arrays and `opTable` stay aligned.
