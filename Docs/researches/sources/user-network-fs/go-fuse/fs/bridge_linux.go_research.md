# sources/user-network-fs/go-fuse/fs/bridge_linux.go

Purpose: Linux-specific `Statx` support for `rawBridge`.

Important functions: `setStatx` mirrors attr defaulting for permissions, UID/GID, and block fields; `setStatxTimeout` applies attr timeout; `Statx` resolves inode/file handle, dispatches to `NodeStatxer` or file statx implementation, then normalizes inode number and mode from stable attrs before returning status.

Control flow/state: reads bridge options and inode stable attrs; no independent persistent state.

Dependencies/integration: depends on Linux `fuse.Statx*` types and `setStatxBlocks` from `files_linux.go`. One apparent risk is the fallback type assertion checks `n.ops.(FileStatxer)` rather than the file handle, so file-level statx may not dispatch as intended unless node ops also implement it. Test signal should include Linux statx tests and loopback statx behavior.
