# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportsrv.c

Implements the core 9P request handlers for `exportfs`. It translates 9P messages into local Plan 9 filesystem operations using `Fid` and `File` state from `exportfs.h`.

Key behavior:
- Negotiates `Tversion`, rejecting non-`9P2000` clients and bounding `messagesize`.
- Rejects `Tauth`; this export path does not require per-session auth.
- Implements attach/walk/clunk/stat/create/remove/wstat locally, including pseudo mount point setup when `srvfd` is active.
- Dispatches potentially blocking `Topen`, `Tread`, and `Twrite` to worker processes through `slave()` and `blockingslave()`.
- Enforces read-only mode both in the central `slave()` gate and in mutating handlers.
- Supports `Tflush` by recording `flushtag`, optionally posting a note to an interruptible worker, then emitting a flush reply.

Important implementation details:
- `clonefid()` forcibly replaces an existing newfid if needed, closing its file descriptor before reallocation.
- `Xwalk()` implements partial walk semantics and prevents walking above the exported root by returning `Exmnt`.
- `Xstat()` rewrites the returned qid path to `f->f->qidt->uniqpath`, preserving exportfs' synthetic path identity.
- `slaveopen()` detects `QTMOUNT` and starts a nested exportfs via `openmount()`.
- `slaveread()` uses `preaddir()` when directory filtering is active through `patternfile`.

Risks and invariants:
- Several comments acknowledge races because the server relies on shared-memory workers and sparse locking.
- Worker interruption is note-based and only active during selected blocking syscalls.
- `openmount()` forks and execs `/bin/exportfs`, so mount traversal depends on the external executable and inherited fd setup.
