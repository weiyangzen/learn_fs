# sources/user-network-fs/samba/source3/modules/vfs_widelinks.c

## Purpose
`vfs_widelinks.c` reintroduces legacy insecure `wide links = yes` behavior as an explicit VFS module. It hides symlink traversal from upper smbd path checks by preserving the logical share-relative current directory and masking symlink semantics for non-POSIX operations.

## Important APIs, Types, and Functions
`struct widelinks_config` stores whether the module is active, whether the share is a DFS root, and the logical `cwd`. `widelinks_connect()` allocates config and checks `lp_widelinks()` and DFS settings. `widelinks_chdir()` records the requested absolute path after the next chdir succeeds. `widelinks_realpath()` returns a canonicalized path based on the logical cwd rather than the underlying filesystem target. `widelinks_lstat()` maps lstat to stat for non-POSIX paths after chdir. `widelinks_openat()` removes symlink-follow prevention flags and handles DFS symlink ENOENT/ELOOP behavior.

## Control Flow
Before the share chdir or when `wide links` is not active, functions pass through to the next VFS module. Once active and after chdir, realpath combines logical cwd plus input path, lstat hides symlinks, and open clears `O_NOFOLLOW`, optional `O_PATH`, and `VFS_OPEN_HOW_RESOLVE_NO_SYMLINKS`. POSIX path requests still see symlinks where lstat is concerned.

## State and Persistence
The only module state is per-connection logical cwd. No on-disk state is changed beyond normal operations performed by the next VFS layer.

## Dependencies and Integration Points
It depends on Samba VFS path operations and loadparm settings `wide links`, `host msdfs`, and `msdfs root`. It exists to isolate insecure share-escape compatibility from core smbd path enforcement.

## Risks
The module intentionally weakens symlink containment and must be enabled only by explicit administrator choice. Incorrect activation before chdir could hide setup-time symlinks, but the code passes through while `cwd == NULL` to fail safer. `openat()` removes no-symlink resolution flags without checking POSIX path flags, so its semantics must match callers' expectations.

## Test Signals
Tests should verify inactive pass-through, pre-chdir pass-through, logical cwd realpath after symlink traversal, lstat-to-stat masking for normal paths, POSIX-path lstat behavior, open flag stripping, and DFS symlink error shaping.
