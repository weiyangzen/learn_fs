# sources/sync-backup/git-lfs/tools/kv/keyvaluestore.go

Purpose: small gob-backed in-memory key/value store with optimistic merge-on-save persistence.

Important APIs/types/functions: `Store`, `NewStore`, `Set`, `Remove`, `RemoveAll`, `Visit`, `Get`, `Save`, `RegisterTypeForStorage`, internal `operation`, `change`, `loadAndMergeIfNeeded`, `loadAndMergeReaderIfNeeded`, and `reapplyChanges`.

Control flow: `NewStore` loads existing gob data when present. Mutations update the map and append to a change log. `Save` opens/creates the file, reloads if the on-disk version differs, replays pending changes onto the disk map, increments version, encodes version then map, truncates old content, and clears the log.

State and persistence: owns an in-memory map, version, change log, and filename; persists via gob. Uses an RW mutex for in-process access but no cross-process file lock despite optimistic conflict detection.

Dependencies and integration points: suitable for lightweight Git LFS metadata caches. Depends on Go `encoding/gob`, `os`, `sync`, Git LFS `errors` and `tr`. Custom stored structs must be registered with gob.

Risks: comment explicitly notes lost-update possibilities beyond read-committed style behavior. Gob schema/type compatibility matters. `Save` ignores the return error from `loadAndMergeReaderIfNeeded` in one path. Truncating before encode completion can leave a corrupt file on write failure.

Test signals: `keyvaluestore_test.go` covers basic types, custom struct registration, remove/remove-all, optimistic conflict merging, and file-size reduction after truncation.
