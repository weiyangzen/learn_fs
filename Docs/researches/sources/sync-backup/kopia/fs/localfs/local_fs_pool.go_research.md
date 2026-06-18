## sources/sync-backup/kopia/fs/localfs/local_fs_pool.go

Purpose: centralizes object pooling for localfs entry wrappers to reduce allocation churn during large tree traversals.

Important APIs/types/functions: pools for filesystem files, directories, symlinks, error entries, and shallow placeholder entries; constructors such as `newFilesystemFile`; `Close` methods returning objects to pools.

Control flow, state, and persistence: constructors take a pooled struct, overwrite its embedded `filesystemEntry`, and return it. `Close` returns the object to `freepool`. No durable state exists, but object identity is reused aggressively.

Dependencies and integration points: depends on `internal/freepool` and all localfs entry types. It relies on callers respecting `fs.Entry.Close` ownership rules.

Risks and test signals: biggest risk is use-after-close or stale fields if future constructors forget to reset new fields. Traversal tests provide indirect coverage; concurrency hazards are controlled by the assumption that a returned entry is not used after close.
