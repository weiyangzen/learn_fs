# sources/storage-engines/wiredtiger/test/format/format_config_def.c

## Purpose
`format_config_def.c` is the generated definition of `CONFIG configuration_list[]`, the ordered schema table that drives parsing, randomization, validation, help/error output, and final config printing.

## Important APIs, Types, And Functions
The file defines only `CONFIG configuration_list[]`. Each entry has a name, description, flags, minimum value, random maximum, explicit maximum, and generated offset. Entries cover assertions, backup, block cache, btree shape, cache, checkpoints, debug/stress flags, disaggregation, disk, logging, operations, prefetch, runs, statistics, tiered storage, transactions, and WiredTiger open settings.

## Control Flow
Consumers iterate from `configuration_list[0]` until the `{NULL, NULL, ...}` sentinel. `format_config.c` uses flags to decide whether entries can be randomized directly, whether they are strings, table-scoped, type-specific, or require special handling.

## State And Persistence Behavior
The list is read-only compiled data. Its order and offsets define the in-memory `CONFIGV` layout for every table. Its descriptions are emitted by `config_error`, and names are emitted by `config_print`.

## Dependencies And Integration Points
It is generated from `config.sh` and must stay synchronized with `format_config.h`. It includes `format.h` to use flags, offset constants, and macros such as `MEGABYTE`, `M`, and `RTS_THREADS_MAX`.

## Risks And Test Signals
Risks include schema/order mismatch, incorrect bounds causing invalid random values, wrong `C_IGNORE` classification bypassing special logic, and feature defaults that create unsupported combinations. Signals are parser failures, warnings during normalization, and compile-time failures when offset names do not exist.
