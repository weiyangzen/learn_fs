# sources/user-network-fs/libfuse/lib/fuse_daemonize_i.h

## Purpose

`fuse_daemonize_i.h` is the private header for libfuse's early daemonization coordination hooks. It exposes only the internal state transitions needed by mount and initialization code while keeping the public daemonization API in `include/fuse_daemonize.h`.

## Important APIs, Types, And Functions

The header declares `fuse_daemonize_early_set_mounted(void)`, `fuse_daemonize_early_is_used(void)`, and `fuse_daemonize_set_got_init(void)`. It includes `<stdint.h>` and `<stdbool.h>` and uses a standard include guard `FUSE_DAEMONIZE_I_H_`.

`fuse_daemonize_early_set_mounted` is documented as called from `fuse_session_mount()`. `fuse_daemonize_set_got_init` records that FUSE_INIT handling happened. `fuse_daemonize_early_is_used` lets other internals detect whether the new early daemonization path is active or has daemonized.

## Control Flow

The header has no executable control flow. Its declarations support the control flow in `fuse_daemonize.c`: early start sets `active`, mount code calls the mounted setter, init handling calls the got-init setter, and success signaling checks both flags before notifying the parent.

## State And Persistence Behavior

No state is defined in this header. The declarations mutate or query the file-global daemonization singleton in `fuse_daemonize.c`. There is no persistence beyond process memory and inherited post-fork state.

## Dependencies And Integration Points

This private header is included by `fuse_daemonize.c` and should be included by internal session or mount code that needs to mark mount/init progress. It should not be treated as a public application header; public callers use `include/fuse_daemonize.h`.

## Risks And Edge Cases

Because this header intentionally exposes only partial daemonization state management, incorrect call placement in mount or init code can make the parent wait forever or exit too early. The functions have no parameters describing which session is being initialized, so the implementation is singleton-oriented rather than per-session.

## Test Signals

Tests should verify that mount code calls `fuse_daemonize_early_set_mounted` exactly after a successful mount and that FUSE_INIT handling calls `fuse_daemonize_set_got_init`. Integration tests for `fuse_daemonize.c` should indirectly validate this header by confirming that early success is not signaled until both internal hooks have run.
