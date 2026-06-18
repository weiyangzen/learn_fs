# sources/sync-backup/restic/internal/fs/interface.go

Purpose: Defines the filesystem abstraction used by backup and restore code.

Important APIs: `FS` and `File` interfaces.

Control flow and state: Interfaces specify path operations, `Lstat`, and `OpenFile` behavior. `OpenFile(metadataOnly=true)` must return a `File` for arbitrary file types and may defer real filesystem access. `File.MakeReadable` transitions metadata-only objects to readable mode; `ToNode` must be consistent with `Stat`.

Dependencies and integration: Implemented by `local`, `reader`, `LocalVss`, and wrappers like `Track`. Integrates with `data.Node` as the persisted metadata model.

Risks: The consistency requirement between `Stat` and `ToNode` is central; implementations must avoid returning metadata for different filesystem states. Only `O_NOFOLLOW` and `O_DIRECTORY` are guaranteed flags.

Test signals: Local and reader tests exercise the interface contract across real and synthetic filesystems.
