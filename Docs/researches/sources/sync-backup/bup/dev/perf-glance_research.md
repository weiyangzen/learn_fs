# sources/sync-backup/bup/dev/perf-glance

## Purpose
Quick manual performance glance for bup init/index/save/restore over supplied source data.

## Important APIs, Types, and Functions
Defines shell helpers `bup()` and `get-time()`, uses repository-local `./bup`, and runs `init`, `index`, `save -t`, and `restore`.

## Control Flow
Creates `test/tmp/perf-glance-*`, sets `BUP_DIR`, times each bup operation with Python `time.time()`, prints durations, and removes the temporary directory.

## State and Persistence Behavior
Creates a temporary bup repository and restore tree under `test/tmp`, then deletes it on normal completion.

## Dependencies and Integration Points
Requires a built `./bup` and source data paths. Useful for comparing performance changes.

## Risks and Test Signals
Risks are no cleanup on interrupted run, wall-clock variability, and source data dependence. Signals are printed operation durations and successful command completion.
