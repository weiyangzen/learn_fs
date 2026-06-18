# sources/sync-backup/casync/src/cafuse.h

## Purpose
Declares the optional FUSE entry point for mounting a `CaSync` archive view.

## Important APIs, Types, and Functions
`ca_fuse_run(CaSync *s, const char *what, const char *where, bool do_mkdir)` runs the read-only FUSE mount for the provided synchronizer, optional filesystem name, mount path, and mkdir flag.

## Control Flow
The header has no logic. Consumers call `ca_fuse_run` after configuring `CaSync`; the implementation owns the mount loop until exit.

## State and Persistence Behavior
No state is declared. The implementation uses the supplied `CaSync` as transient process state and does not persist data.

## Dependencies and Integration Points
Includes `casync.h` for `CaSync`. Consumed by `casync-tool.c` under `HAVE_FUSE`.

## Risks
The header is tiny, so the main risk is build-configuration mismatch: callers must only link this when FUSE support is compiled.

## Test Signals
Compile with and without `HAVE_FUSE`, and command-line mount path coverage through `casync-tool.c`.
