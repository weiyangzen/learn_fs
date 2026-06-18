# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/fsck.h

Read coverage: complete file read, 136 lines.

Purpose: central state and utility definitions for `fsck.ocfs2`.

Key data:
- `o2fsck_resource_track` stores elapsed/user/system time and I/O stats.
- `o2fsck_state` holds the filesystem handle, cached allocator inodes, inode and cluster bitmaps, inode-count tables, directory block and parent indexes, refcount tracking state, prompt/repair flags, error/status flags, progress state, and filesystem object counters.
- Defines `OCFS2_MAX_PATH_DEPTH` histogram size for extent depths.

Key API: `o2fsck_state_reinit()` and verbose logging macro.

Dependencies: inode-count and directory-block headers plus tools progress API.

Risk notes:
- Most fsck modules mutate shared `o2fsck_state`; correct pass ordering is required.
- Prompt flags and write-error flags are global to a run.
