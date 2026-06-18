# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/console.c

Console-side wrappers around the 9P1 request handlers, plus console-only `fstat` and `clri` operations.

Key responsibilities:
- `fcall9p1()` validates a 9P1 request type, enters `mainlock`, runs the appropriate `call9p1[]` handler under the channel ref lock, and records an error in the reply.
- Provides simple helpers: `con_session`, `con_attach`, `con_clone`, `con_walk`, `con_open`, `con_read`, `con_write`, `con_remove`, `con_create`.
- `doclri()` forcibly clears a directory entry after checking parent and target phase conditions.
- `f_fstat()` prints a selected file's dentry fields, direct block list, indirect block pointers, qid, size, and times.
- `f_clri()` wraps `doclri()` as a console operation.
- `con_clri()` and `con_fstat()` call the custom console handlers directly under locks instead of going through `call9p1`.

Important interactions:
- Uses `9p1.h` `Fcall` and `call9p1[]`.
- Uses console-global `cons.uid` and `cons.gid` as an explicit "beyond ugly" side channel for `con_create`.
- Uses dentry/block functions: `getbuf`, `getdir`, `checktag`, `accessdir`, `freewp`, `freefp`.

Research notes:
- `doclri()` refuses read-only devices and requires a valid parent `Wpath`.
- `f_fstat()` is diagnostic output only; it does not pack a protocol stat reply.
- `con_read()`/`con_write()` return 0 on protocol error, making short read/write indistinguishable from error for callers unless they inspect command output.
