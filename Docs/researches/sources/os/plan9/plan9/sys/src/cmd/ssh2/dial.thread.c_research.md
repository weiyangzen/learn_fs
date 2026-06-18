# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.thread.c

This file is the thread-library-safe parallel `dial` implementation used where `rfork(RFMEM|RFPROC)` is unsuitable.

Key behavior:
- Keeps the same dial-string parsing, `/net` to `/net.alt` fallback, `/net/cs` lookup, clone/control write, and data-open behavior as `dial.c`.
- Uses Plan 9 thread procs (`proccreate`) and channels instead of shared-memory rfork children.
- Sends result tuples containing data fd, ctl fd, connection directory, or error back to the parent.
- Interrupts losing connection attempts with `threadint`.

Important details:
- `Dest` owns a bounded `kidthrids[64]` array, so excess translated addresses are ignored.
- The first successful data fd wins; later successes are closed.
- The implementation explicitly initializes returned `cfdp` and `dir` to safe empty values before dialing.
- Shared mutable connection result state is minimized compared with `dial.c`.

Filesystem relevance:
- Direct: provides threaded clients a safe way to operate Plan 9 network namespace files such as `/net/cs`, `clone`, `ctl`, and `data`.
