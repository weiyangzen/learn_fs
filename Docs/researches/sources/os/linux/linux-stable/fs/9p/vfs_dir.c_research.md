# File Research: sources/os/linux/linux-stable/fs/9p/vfs_dir.c
- Purpose: Implements 9P directory file operations.
- Main functions: `v9fs_dir_readdir`, `v9fs_dir_readdir_dotl`, `v9fs_dir_release`.
- Legacy readdir: Reads raw 9P stat records with `p9_client_read`, decodes them, maps 9P mode bits to `DT_*`, and emits VFS dirents.
- Dotl readdir: Uses `p9_client_readdir` and `p9_dirent` data for Linux 9P2000.L directory entries.
- Release behavior: Clunks/drops the directory FID and frees readdir buffer state.
- Operation tables: Exports `v9fs_dir_operations` and `v9fs_dir_operations_dotl`.
- Risks: Directory offsets and partial record handling must remain consistent across repeated `iterate_shared` calls.
