# sources/user-network-fs/rclone/cmd/bisync/lockfile.go

Purpose: Provides per-session lock-file creation, expiration, renewal, removal, and failure marking so two bisync runs over the same paths do not overlap.

Important APIs/types/functions: `basicallyforever` represents no practical expiration. `lockFileOpt` stores renewal stopper and JSON lock metadata. `setLockFile`, `removeLockFile`, `setLockFileExpiration`, `renewLockFile`, `lockFileIsExpired`, `startLockRenewal`, and `markFailed` implement lock lifecycle.

Control flow: `setLockFile` clamps `--max-lock`, skips locks in dry-run, derives `<basePath>.lck`, rejects a present non-expired lock, writes the current PID, rewrites it as JSON metadata, and starts background renewal when expiration is finite. `lockFileIsExpired` opens and decodes existing JSON; unreadable files expire only when finite max-lock is configured, and expired/unreadable locks mark listings failed so recovery or resync is required. `removeLockFile` stops renewal before deleting.

State and persistence behavior: The lock file is persisted as JSON containing session, PID, renewal time, and expiration time. Expired/unreadable lock handling renames current listings to `-err` via `markFailed`, deliberately invalidating potentially unsafe state. Renewal rewrites the lock file at `max-lock - 1 minute` intervals.

Dependencies and integration points: Called by `Bisync` around `runLocked` and from atexit signal handling. Uses `bilib.FileExists`, secure file permissions, terminal-colored diagnostics, and `prettyprint` for lock info.

Risks: Lockfiles protect only sessions that share the same canonical `basePath`. Unreadable legacy or corrupt lockfiles without `--max-lock` block forever by design. Renewal uses goroutine lifecycle and must always be stopped before removal. Marking listings failed is conservative but may surprise users after an expired stale lock.

Test signals: `lockfile_test.go` directly covers unreadable with/without max-lock and expired/not-expired JSON. Additional useful tests include max-lock clamping, dry-run no-lock behavior, renewal stop behavior, and lock contention messages.
