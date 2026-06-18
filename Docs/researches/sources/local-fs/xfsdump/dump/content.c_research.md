# File Research: sources/local-fs/xfsdump/dump/content.c

`content.c` is the main xfsdump content engine. It owns dump initialization, incremental/resume decision logic, inode map integration, per-stream dump execution, media-file lifecycle, inventory updates, directory/non-directory serialization, extended attribute serialization, HSM hooks, and quota snapshot handling.

Key responsibilities:
- Parses dump-specific options from `GETOPT_CMDSTRING`, including level, subtree, resume, base session UUID, inventory update suppression, media erase, media alert program, extended attributes, HSM offline mode, skip-unchanged-dirs, exclude files, and max dump file size.
- Resolves the source filesystem via `fs_info`, confirms it is mounted, verifies the mountpoint is the filesystem root via `check_rootdir`, opens the root, obtains root `xfs_bstat`, and builds a JDM filesystem handle.
- Consults the inventory to determine incremental base sessions and interrupted same-level sessions for resume ranges.
- Calls `inomap_build` to classify inodes and calculate stream startpoints, then calls `var_skip` to remove xfsdump’s own state directory from the dump if it lives on the target filesystem.
- Initializes content header fields such as dump level, flags, root inode, inomap metadata, incremental/resume UUIDs, and checksum/format capabilities.
- Allocates per-stream `context_t` buffers for file headers, extent headers, directory entries, extended attributes, symlink reads, HSM file context, and inomap iteration context.

Main data structures:
- `mark_t`: wraps a drive-layer mark with an xfsdump `startpt_t`; committed marks update restart positions in the stream content header.
- `context_t`: per-stream state and scratch buffers, including media file size, committed mark count, current progress inode, completion flag, first media label, and media begin/end protocol state.
- `extent_group_context_t`: holds `XFS_IOC_GETBMAPX` state for regular-file extent dumping.
- `pds_t`: per-drive progress/status phase for status-line reporting.

Dump flow:
- `content_stream_dump` drives one stream. It writes an inomap to every media file, optionally writes the directory dump on stream 0, then iterates non-directories from the current startpoint.
- For each media file it calls `Media_mfile_begin`, writes content, places marks, writes a null file header, ends the media file with `Media_mfile_end`, and updates inventory media-file records.
- When drives support multiple media files, streams synchronize before dumping session inventory and writing a stream terminator.

File serialization:
- Directories are dumped by `dump_dirs` and `dump_dir`, using bulkstat and `getdents_wrap`. Directory entries are serialized by `dump_dirent`, with compatibility support for old v1 dirent headers.
- Regular files are dumped by `dump_file_reg`. It splits large files into extent groups, sets media marks at restart boundaries, writes file and extent headers, handles holes explicitly, aligns large/realtime extents, reads file data, and zero-pads short reads to match already-written extent headers.
- Special files and symlinks are dumped by `dump_file_spec`; symlinks store their target as a data extent.
- Extended attributes are dumped via `jdm_attr_list` and `jdm_attr_multi` across non-root, root, and secure namespaces. Records are built in `dump_extattr_buildrecord` and terminated by a null extattr header.
- Header writers calculate checksums before byte-order translation via `xlate_*` helpers.

Media handling:
- `Media_mfile_begin` is a state-machine/coroutine style routine with `goto` phases for positioning, erase, media change, and write.
- It handles blank media, foreign/corrupt data, overwrite prompts, stream terminators, append restrictions, removable media change prompts, media labels, and alert-program execution.
- `Media_mfile_end` flushes writes and updates the next expected begin state (`BES_ENDOK`, `BES_ENDEOM`, or invalid).

Inventory and completion:
- `create_inv_session` opens inventory database/session/stream records.
- `inv_cleanup`, registered with `atexit`, closes stream/session/database tokens and marks interrupted streams.
- `content_complete` reports final dump size and removes temporary quota files only on complete dumps.

Security and maintenance notes:
- `save_quotas` builds and executes an `xfs_quota` command with `sprintf` and `system`; mountpoints and generated paths flow into a shell command, making this a command-injection-sensitive path if untrusted names can reach it.
- `media_change_alert_program` is also executed with `system`, intentionally user-controlled by option.
- Many allocations are checked with `assert`, so release builds may not handle allocation failure gracefully.
- Heavy global state (`sc_*`) means the module assumes the established xfsdump process/thread model rather than being reentrant.
- Media synchronization uses sleep polling on global counters and flags.
