# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.c

## Purpose
This is the main driver for the cursor-order stress test. It runs append inserter and reverse scanner workloads to validate cursor ordering for row-store and variable-length column-store files.

## Important APIs, Types, and Functions
- Uses `SHARED_CONFIG` from `cursor_order.h`.
- Parses local options for connection config, multiple files, home, key count, log file, operation counts, scanner/writer counts, run count, file type, and workload variation.
- `wt_connect` recreates the home and opens WiredTiger with statistics logging and optional caller config.
- `wt_shutdown` checkpoints and closes the connection.
- `shutdown` removes the work directory.
- Event handlers route errors to stderr and messages to a log file or stdout.

## Control Flow
`main` initializes default shared config, parses options, validates that varying operation counts require multiple files, installs SIGINT cleanup, then loops for the requested number of runs. Each run removes prior home state, opens a connection, calls `ops_start(cfg)` to perform the workload, and checkpoints/closes. Run count `0` means continuous.

## State and Persistence Behavior
Each run creates a fresh WiredTiger home, loads/operates on files through helper modules, checkpoints at shutdown, and removes the home at the start of the next run or on interrupt. Optional log file captures WiredTiger messages.

## Dependencies and Integration Points
The driver depends on `load`, `ops_start`, and `verify` functions from sibling files. It integrates with CTest variants through `-tr` and `-tv`. It uses `testutil_work_dir_from_path` and direct `__wt_getopt` parsing.

## Risks and Test Signals
Failures surface through testutil assertions, invalid option usage, or workload helper errors. Infinite runs are possible with `-r 0`, so smoke variants use defaults. Interrupt cleanup removes the home and exits failure.
