# sources/sync-backup/kopia/repo/refcount_closer.go

Purpose: coordinates cleanup of shared repository resources when the last repository or writer reference closes.

Important APIs/types/functions: `closeFunc` is a context-aware cleanup callback. `refCountedCloser` holds atomic `refCount`, atomic `closed`, and ordered `closers`. Methods are `Close`, `addRef`, `registerEarlyCloseFunc`, and constructor `newRefCountedCloser`.

Control flow: new closers start with one reference. Each writer clone calls `addRef`. `Close` decrements the count and returns immediately unless it reaches zero. On final close, it panics if already closed, marks closed, invokes all cleanup functions, and returns `errors.Join` of their results. `registerEarlyCloseFunc` prepends a cleanup function by wrapping it into the front of the closer list.

State and persistence behavior: in-memory lifecycle state only. It controls persistent resource flushing/closing indirectly by invoking registered storage, metrics, diagnostics, and cache closers.

Dependencies/integration: used by direct and server repository parameter structs in `open.go`/`repository.go`. Depends on standard `sync/atomic` and `errors.Join`.

Risks: extra `Close` calls after the count reaches zero can decrement negative and avoid the already-closed panic path; callers must balance references. Registering early close functions mutates the slice without synchronization, so it should happen during setup.

Test signals: repository writer-scope and close-path tests indirectly exercise reference balancing; no direct unit tests in this file.
