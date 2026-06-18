# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/proc_paths.rs

This file implements path discovery through `/proc/self/fd` for passthrough filesystem migration. It is part of preserialization: it fills or repairs `InodeMigrationInfo` so serialized state can describe how the destination should find inodes.

Key structures:
- `Walker`: shared implementation for all modes; holds `&PassthroughFs`, a `Mode`, and an optional cancellation flag.
- `Constructor`: best-effort preserialization path builder for `--migration-mode=find-paths`.
- `ConfirmPaths`: explicit `--migration-confirm-paths` checker; returns hard errors to block migration.
- `ImplicitPathCheck`: lax post-preserialization double-check; logs warnings instead of failing migration.
- `WrappedError`: separates `Fallback` errors, where exhaustive path search might work, from `Unrecoverable` errors.

Main flow:
- `Walker::run()` obtains the root node and the shared directory path from the root inode's `/proc/self/fd` symlink, then iterates `fs.inodes`.
- Cancellation is honored between inode visits through an `AtomicBool`.
- `should_update_inode()` decides whether to create migration info, leave existing info alone, or clear and refresh bad path info.
- `set_path_migration_info_from_proc_self_fd()` reads an inode's absolute `/proc/self/fd` path, derives a path relative to the shared directory, walks each component through `fs.do_lookup()`, and attaches `InodeMigrationInfo` along the path.

Important behavior:
- Root absence is allowed only when the inode store is empty; otherwise it is treated as unrecoverable.
- Deleted `/proc/self/fd` targets with positive link count and paths outside the shared root with multiple links trigger fallback, because a hard link inside the shared directory may still exist.
- `InodePathError::NoFd` is unrecoverable; most other `FdPathError`s are fallback candidates.
- Non-UTF-8 relative paths are unrecoverable because serialized path locations use `String`.
- If component traversal succeeds but does not end at the intended inode, the caller is advised to fall back.

Interactions:
- Uses `InodeData::get_path()`, `statx()` link counts, `relative_path()`, `StrongInodeReference`, and `PassthroughFs::do_lookup()`.
- Feeds `device_state::serialization.rs` by ensuring `InodeData.migration_info` is present where possible.
- Used again by `passthrough/mod.rs` after path-invalidating operations to rediscover moved or hard-linked inodes.

Edge cases and risks:
- Path discovery is inherently race-prone; the surrounding migration code mitigates this with confirm and implicit check phases.
- `/proc/self/fd` may report deleted, anonymous, or outside-root paths, so fallback classification is central to correctness.
- The relative path helper is byte-prefix based; callers depend on root identity and later lookup verification to avoid accepting wrong sibling paths.
