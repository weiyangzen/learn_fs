<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock.go -->
# sources/sync-backup/kopia/tests/robustness/pathlock/path_lock.go

This file implements path-scoped mutual exclusion for FIO filesystem operations. `Locker` returns an `Unlocker`; `pathLock` maintains a map from cleaned paths to lock channels plus a mutex. It rejects overlapping locks so a parent and child path cannot be modified concurrently.

`Lock` cleans paths and spins until `tryToLockPath` succeeds, incrementing `busyCounter` for test observability. `tryToLockPath` checks every currently locked path with `isInPath` in both directions, then creates a channel marker. `Unlock` closes/removes the channel. `isInPath` uses `filepath.Rel` and rejects paths that start with `..`.

State is process-local and synchronized by `sync.Mutex`; `busyCounter` is atomic for tests. Dependencies are filepath normalization and string prefix checks. Risks include busy waiting without context cancellation, path comparison edge cases with symlinks/case-insensitive filesystems, and panic potential from double unlock avoided only by ownership discipline. Tests cover basic, nonblocking, and race behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock.go -->
