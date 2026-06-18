# File Research: sources/local-fs/e2fsprogs/e2fsck/ehandler.c

## Purpose
Installs I/O read/write error handlers for an e2fsck session.

## Main Behavior
- Multi-block read/write errors are decomposed into single-block operations to isolate the failing block.
- Single-block read errors are reported with optional current operation text.
- Read errors can be ignored, and if ignored the user can force a rewrite of the block unless it is beyond filesystem end.
- Write errors can be ignored interactively.
- `preenhalt()` is called before prompting, preventing automatic preen from silently continuing through serious I/O errors.
- `ehandler_operation()` sets/restores the global operation description.
- `ehandler_init()` assigns handlers to an `io_channel`.

## Integration
Works through libext2fs `io_channel` callbacks. Uses `ctx` via `fs->priv_data`.

## Risks / Notes
The current operation string is static global state, not per-context.
