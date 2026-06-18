# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbsharedfile.c

Tracks open shared files, share-deny state, byte-range locks, and delete-on-close behavior.

Key functions:
- `smbsharedfileget` finds or creates a shared-file entry by Plan 9 file identity (`type`, `dev`, `qid.path`), enforces current share-deny conflicts, updates aggregate share state, and refs the entry.
- `smbsharedfileput` decrefs, subtracts share state, deletes file on close when requested, frees lock list, and removes entries.
- `smbsharedfilelock` inserts nonconflicting byte-range locks in order.
- `smbsharedfileunlock` removes an exact lock owned by session/pid/range.
- Helpers convert among share mode, deny-read/deny-write booleans, and aggregate share state.

Interactions:
- Used by open/create, close, locking, and delete-on-close related paths.

Notable details:
- `sharesplit` case `SMB_OPEN_MODE_SHARE_DENY_WRITE` assigns `*denywrite` twice and never sets `*denyread`, which appears to be a bug.
- Lock conflict detection is interval based: `[base, limit)`.
