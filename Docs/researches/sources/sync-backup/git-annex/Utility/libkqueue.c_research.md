<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.c -->
# sources/sync-backup/git-annex/Utility/libkqueue.c

Purpose: a tiny BSD kqueue C helper library used by git-annex code that wants a minimal file-descriptor change notification interface. It watches vnode write events on already-open file descriptors and exposes a small C ABI rather than requiring the caller to manage `struct kevent` setup directly.

Important APIs and functions: `helper(kq, fdcnt, fdlist, nodelay)` builds a variable-length `struct kevent chlist[fdcnt]`, registers each supplied descriptor with `EVFILT_VNODE`, `EV_ADD | EV_ENABLE | EV_CLEAR`, and `NOTE_WRITE`, then calls `kevent`. `init_kqueue()` creates the queue with `kqueue()` and exits after `perror` on failure. `addfds_kqueue()` registers descriptors by calling `helper` with a zero timeout. `waitchange_kqueue()` blocks by calling `helper` with no changelist and no timeout.

Control flow: callers first call `init_kqueue`, call `addfds_kqueue` one or more times to add descriptors, then call `waitchange_kqueue` to receive the changed descriptor identifier. `helper` returns `evlist[0].ident` only when exactly one event is returned; zero events, errors, and unexpected multi-event results collapse to `-1`.

State and persistence: watched descriptors are held by the kernel kqueue across calls; the C file has no heap allocations or persistent user-space state. File descriptor lifetime remains owned by the caller.

Dependencies and integration points: BSD/macOS kernel APIs from `<sys/event.h>` and `<sys/time.h>`, plus standard C/POSIX headers. The Haskell or C FFI side is expected to link this file and use the ABI declared in `libkqueue.h`.

Risks: `struct kevent chlist[fdcnt]` is a C99 variable-length stack allocation and does not handle negative or very large counts defensively. `helper` ignores `errno` and conflates timeout/no event with real errors. It only watches `NOTE_WRITE`, so rename/delete/attribute changes are outside this helper's scope. `init_kqueue` terminates the process on failure instead of returning an error code.

Test signals: useful tests should exercise kqueue creation, registering a directory or file descriptor, detecting a write, timeout behavior from `addfds_kqueue`, and handling closed descriptors. Platform tests must be limited to systems with kqueue support.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.c -->
