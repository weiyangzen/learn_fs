## sources/sync-backup/restic/internal/fuse/other.go

Purpose: fallback FUSE node for non-regular, non-directory, non-symlink snapshot node types such as devices or FIFOs.

Important APIs/types: `other` stores `root`, `forget`, `node`, and `inode`. `newOther` constructs it. `Readlink` returns `node.LinkTarget`, which may matter for special node metadata. `Attr` exposes inode, mode, optional original UID/GID, timestamps, and link count. `Forget` triggers cache eviction.

Control flow and state: this is a lightweight metadata-only node. It does not implement open/read or xattrs, so the mounted representation is primarily a stat/readlink surface.

Dependencies and integration points: constructed from FUSE directory lookup when a `data.Node` does not map to file, dir, or symlink. It integrates with `Root.cfg.OwnerIsRoot` and `treeCache` forget callbacks.

Risks and test signals: behavior for special files is platform-sensitive and this file has less direct coverage than file/link/dir paths. Incorrect mode or ownership can change how tools classify restored special nodes. Coverage is indirect through FUSE tests and inode tests.
