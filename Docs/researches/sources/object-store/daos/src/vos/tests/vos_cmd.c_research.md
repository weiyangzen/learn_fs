# sources/object-store/daos/src/vos/tests/vos_cmd.c

## Purpose
Implements the `vos_tests -r` command mini-language for creating/opening VOS pools, writing and removing extents, punching dkeys, iterating data, aggregating, discarding, querying size, and running randomized stress operations.

## Important APIs, types, and functions
- `struct known_pool` tracks pool name/path/UUID and open pool/container handles.
- `struct cmd_info` stores parsed key, start, length, operation type, and status.
- Operations include `create_pool`, `open_pool`, `close_pool`, `write_key`, `punch_key`, `discard`, `aggregate`, `iterate`, `visible_iterate`, `print_size`, and `run_many_tests`.
- Argobots helpers `abit_start`, `handle_op`, and `ult_func` run operations in ULTs.

## Control flow
`run_vos_command` splits the command string into argv, parses long/short options into an array of `cmd_info`, starts Argobots, then runs a single cmocka test executing commands sequentially. Synchronous operations are joined immediately; randomized stress launches async ULTs for 30 seconds, periodically joins completed operations, and asserts every status is zero.

## State and persistence behavior
State includes global known pool list, current open pool, newest write epoch, operation share table, write buffer, and ULT lists. Pool files are created under `vos_path` with deterministic UUIDs derived from pool names. `--destroy_all` controls whether created/opened pool files are destroyed at cleanup.

## Dependencies and integration points
Depends on VOS object/pool/container/iterator APIs, Argobots, DAOS list/atomic/error helpers, `vts_io.h`, and the full `vos_tests.c` launcher. It exercises VOS API behavior through user-specified scenarios and randomized aggregation/yield interleavings.

## Risks and edge cases
The command splitter is whitespace-based and does not support quoting inside command values. `create_pool` preallocates 4 GiB files, which may be expensive or fail on constrained filesystems. Randomized tests are time-based and seed-logged but nondeterministic. Global `current_open` permits only one open pool/container at a time.

## Test signals
Signals include cmocka assertion success, zero VOS return codes, visible/covered iteration output, operation-count table for randomized runs, and cleanup of pool handles/files when requested.
