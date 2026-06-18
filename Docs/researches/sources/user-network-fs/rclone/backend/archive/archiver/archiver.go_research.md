# sources/user-network-fs/rclone/backend/archive/archiver/archiver.go

Purpose: Defines the registry used by archive format implementations to plug into the archive backend.

Important APIs/types/functions: `Archiver` struct contains `New func(ctx, f, remote, prefix, root) (fs.Fs, error)` and `Extension string`. Package-global `Archivers []Archiver` stores registered implementations. `Register` appends one or more archivers.

Control flow: Concrete packages call `archiver.Register` in `init`. `archive.go` scans `Archivers` to detect file extensions and instantiate the matching archive Fs lazily.

State and persistence: Global in-process registry; append order follows package initialization order.

Dependencies and integration points: Depends on rclone `fs` and context. Used by `backend/archive/zip` and `backend/archive/squashfs`.

Risks: Registry is a mutable slice with no locking; it is safe during init but not designed for concurrent runtime modification. Extension matching is suffix-based and linear.

Test signals: Archive tests indirectly validate that zip and squashfs are registered and discoverable.
