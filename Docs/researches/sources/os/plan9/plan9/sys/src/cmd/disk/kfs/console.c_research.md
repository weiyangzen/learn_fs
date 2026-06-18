# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/console.c

This file lets internal KFS commands invoke filesystem operations through the same 9P1 handler path used by clients.

Key behavior:
- `fcall9p1` wraps a 9P1 operation with `mainlock` and channel `reflock`, dispatching via `call9p1`.
- Provides wrappers: `con_session`, `con_attach`, `con_clone`, `con_path`, `con_walk`, `con_stat`, `con_wstat`, `con_open`, `con_read`, `con_write`, `con_remove`, `con_create`.
- `con_create` sets `cons.uid` and `cons.gid` before calling `Tcreate9p1`, enabling console-selected ownership.
- Implements `doclri`, `f_clri`, and `con_clri` to clear a directory entry without normal truncation/removal semantics.
- `con_swap` swaps two dentries’ contents while preserving their names, used by cross-directory rename logic in `con.c`.

Dependencies:
- Uses `Oldfcall`, `call9p1`, and 9P1 message constants.
- Calls core metadata helpers `getbuf`, `getdir`, `mkqid`, `freewp`, `freefp`, and `accessdir`.

Notable details:
- Console operations intentionally reuse server code paths, reducing duplicate permission and metadata behavior.
- `clri` is more dangerous than regular remove because it clears a dentry directly.
