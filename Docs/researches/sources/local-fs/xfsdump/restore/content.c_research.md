# File Research: sources/local-fs/xfsdump/restore/content.c

## Role

`content.c` is the main restore-content engine for `xfsrestore`. It coordinates command-line restore policy, persistent housekeeping state, dump selection, media traversal, directory-tree reconstruction, non-directory file restore, extended attributes, multi-stream synchronization, resume support, and final cleanup.

The file is stateful and central: it wires together drive/media I/O, inventory, inomap, tree, namreg, dirattr, logging/dialog, and restore-format translation.

## Major Responsibilities

- Parse restore options and initialize persistent housekeeping under `xfsrestorehousekeepingdir`.
- Validate restore compatibility for normal, cumulative, resumed, and force-complete sessions.
- Maintain an mmap-backed persistent restore state file named `state`.
- Coordinate multiple restore stream threads through `t_sync1` through `t_sync5`.
- Select the target dump session from online inventory, on-media inventory, or operator prompt.
- Traverse media objects/files, including removable media changes, rewinds, end-of-media/data, and inventory files.
- Restore directory hierarchy first, then post-process tree selection, then restore non-directory files concurrently.
- Defer directory attributes until after non-directory restore.
- Restore regular files, special files, sockets, symlinks, hard links, xattrs, timestamps, owners, modes, and XFS inode flags.
- Track partially restored multi-stream regular files so post-data metadata and DMAPI xattrs are applied only when the full file is complete.
- Clean up or preserve housekeeping depending on cumulative/resumable restore state.

## Key Data Structures

- `struct pers`: mmap-backed persistent state. It contains:
  - `v`: housekeeping format magic/version/pagesize.
  - `a`: accumulated restore policy/history, destination, subtree args, partial-file registry.
  - `s`: current session state, progress stats, persistent media inventory, phase completion flags.
- `struct tran`: transient per-process state such as start time, housekeeping directory, sync gates, initialized-subsystem flags, and persistent-inventory lock.
- `struct Media`: per-stream media position wrapper around drive/global/media/content headers. Tracks media-file position states like `POS_ATHDR`, `POS_INDIR`, `POS_ATNONDIR`, `POS_END`, `POS_USELESS`, and `POS_BLANK`.
- `pers_strm_t`, `pers_obj_t`, `pers_file_t`: persistent inventory descriptors for streams, media objects, and media files. They are allocated out of page-sized descriptor space and referenced through `dh_t` handles.
- `partial_rest_t`: tracks restored byte spans for split regular files across restore streams.

## Initialization Flow

`content_init()` is the entry point. It:

- Allocates `tranp`, persistent-inventory lock, and records VM budget/start time.
- Parses restore options including TOC-only, cumulative, resume, overwrite policy, subtree filters, interactive mode, xattr control, workspace directory, dump label/session ID, media alert program, root permission handling, and compatibility flags.
- Validates combinations such as TOC with resume/cumulative, resume without interrupted state, non-cumulative reuse of housekeeping, and option reuse during cumulative/resumed sessions.
- Creates or opens the housekeeping directory and `state` file.
- mmaps and validates persistent format fields: `HOUSEKEEPING_MAGIC`, `HOUSEKEEPING_VERSION`, and page size.
- Handles forced completion of an interrupted restore by syncing `dirattr`, `namreg`, `inomap`, and `tree`, then calling `finalize()`.
- Resizes/remaps the persistent state for subtree descriptors and descriptor pages.
- Records initial destination, XFS-ness, cumulative policy, overwrite policy, owner policy, xattr policy, and subtree descriptors.
- Initializes xattr buffers, libhandle cache for XFS destinations, persistent inventory mapping, dirattr/namreg/inomap/tree sync as appropriate, and media-change flags.

## Restore Thread Flow

`content_stream_restore()` is the per-stream driver. Its phases are:

1. Set cwd to restore destination and initialize per-stream `Media_t` and `stream_context_t`.
2. Use `Inv_validate_cmdline()` once across streams to identify a dump from online inventory if possible.
3. If needed, search media with `Media_mfile_next(PURP_SEARCH)` and select/confirm a dump through ID, label, compatibility rules, or operator prompt.
4. Coordinate directory dump restore through `t_sync3`; one stream initializes `dirattr`, `namreg`, and `tree`, then calls `applydirdump()`.
5. Coordinate tree post-processing through `t_sync4`; one stream calls `treepost()`.
6. Restore non-directory media files concurrently with `Media_mfile_next(PURP_NONDIR)` and `applynondirdump()`.
7. Coordinate final processing through `t_sync5`; one winning stream waits for other streams and calls `finalize()`.

The sync variables are simple enum gates (`SYNC_INIT`, `SYNC_BUSY`, `SYNC_DONE`) guarded by global locks plus sleeps.

## Directory Dump Restore

`applydirdump()`:

- Detects file, dirent, and extattr checksum availability from content inode dump attributes.
- Marks old tree refs as unreferenced once.
- Restores the persistent inode map with `inomap_restore_pers()`.
- Reads directory file headers until a null header or first non-directory header.
- For directory xattr pseudo-files, calls `restore_extattr(..., isdirpr=TRUE, dah=<last dir handle>)`.
- For normal directories, calls `tree_begindir()`, receives a `dah_t` directory attribute handle, reads dirents with `read_dirent()`, and adds entries with `tree_addent()`.
- Flushes `dirattr`, maps `namreg`, optionally fixes root, and marks `dirdonepr`.

`eatdirdump()` is a positioning helper that consumes the inomap/directory portion without populating restore structures. It is used when a stream needs to advance to non-directory content and cannot use drive marks.

## Tree Post-Processing

`treepost()` runs after directory dump ingestion and before non-directory restore. It:

- Optionally checks tree consistency under `TREE_CHK`.
- Adjusts directory-entry reference flags through `tree_adjref()`.
- Sanitizes the inode map for subtree/interactive restores.
- Applies command-line subtree include/exclude descriptors.
- Runs interactive subtree selection if requested.
- Calls `tree_post()` to materialize/prepare the tree.
- Applies deferred directory extended attributes through `tree_extattr(restore_dir_extattr_cb, path1)`.
- Marks `treepostdonepr`.

## Non-Directory Restore

`applynondirdump()` restores file headers from a media file until a null file header or media end. It:

- Brackets needed extent groups with `pi_bracketneededegrps()` for stats and resume behavior.
- Keeps a per-stream current file context. When inode changes, it completes the previous regular file via `restore_complete_reg()`.
- Calls `restore_file()` for the first header of an inode.
- Routes following xattr headers to `restore_extattr()`.
- Routes following extent groups to `restore_extent_group()`.
- Handles corruption by advancing to the next drive mark when possible.
- Checkpoints progress into persistent inventory with `pi_checkpoint()` after each non-null file header.

`restore_file()` delegates hard-link iteration to `tree_cb_links()`. Its callback `restore_file_cb()` performs the actual type-specific restore on the first link and creates hard links for subsequent links.

## File-Type Restore Details

- Regular files:
  - `restore_reg()` opens/creates and truncates to dumped size.
  - Owner is set before xattrs when possible because ownership changes can strip capabilities.
  - XFS inode flags except `POST_DATA_XFLAGS` are set before data restore.
  - `restore_extent_group()` reads extent headers until `EXTENTHDR_TYPE_LAST`, skips align records, ignores holes, and restores data extents.
  - `restore_complete_reg()` waits for full-file completion via partial registry, then applies times, owner if not already done, mode, and post-data XFS flags.
- Special files:
  - `restore_spec()` handles block devices, char devices, FIFOs, and UNIX sockets via `mknod()` or `socket()`/`bind()`, then owner/mode/times.
- Symlinks:
  - `restore_symlink()` reads one data extent as link target, creates the symlink with a temporary umask, and optionally `lchown()`s it.
- Hard links:
  - Subsequent callback invocations unlink the target path if possible and call `link(path1, path2)`.

TOC-only mode prints paths instead of creating files.

## Extent and Header Reading

The read helpers wrap drive read callbacks and translate on-media structures to host format:

- `read_filehdr()` uses `xlate_filehdr()` and validates optional file-header checksums.
- `read_extenthdr()` uses `xlate_extenthdr()` and validates optional extent checksums.
- `read_dirent()` supports current and v1 dirent formats, validates optional checksums, then reads name tail data.
- `read_extattrhdr()` uses `xlate_extattrhdr()` and handles both current and old-style checksum flags.
- `discard_padding()` consumes alignment bytes.
- `restore_extent()` reads media buffers and writes them to the file, retrying ENOSPC by `fdatasync()` then `sync()` before giving up on writes but continuing to drain media.

## Extended Attributes

`extattr_init()` allocates one aligned xattr buffer per drive.

`restore_extattr()` reads an xattr stream until a null xattr header. If xattrs are disabled, TOC-only, or read-only positioning is requested, it only drains media. Otherwise:

- Directory xattrs are recorded into `dirattr_addextattr()` for delayed application.
- Non-directory xattrs are applied only if `partial_check()` says the file is fully restored.
- `setextattr()` maps dump flags to `ATTR_ROOT`, `ATTR_SECURE`, or default namespace and calls `attr_set(..., ATTR_DONTFOLLOW)`.
- DMAPI root attributes with `SGI_DMI_` prefix can still be restored when normal xattr restore is disabled.

Directory xattrs are later replayed through `restore_dir_extattr_cb()` and `dirattr_cb_extattr()`.

## Media Traversal

`Media_mfile_next()` is the central media-selection state machine. Depending on `PURP_SEARCH`, `PURP_DIR`, or `PURP_NONDIR`, it:

- Begins reads with drive ops, handles drive error classes, and tracks current position.
- Returns all files while searching, but only target dump-session files for directory/non-directory phases.
- Detects dump-session transitions, inventory files, terminators, EOD/EOM, blank/useless media, and foreign/corrupt media.
- Adds seen media files to the persistent inventory via `pi_addfile()`.
- Uses persistent inventory queries to decide whether rewinding, continuing, skipping, or requesting new media is useful.
- Positions non-directory restore at the needed file header via saved marks, next-mark seek, or by consuming the directory dump.
- Builds lists of needed media objects for dialogs.
- Supports multi-drive media-change acknowledgement through `mcflag[]` and `content_media_change_needed`.

`Media_end()` closes an active media read when the state indicates one is open.

## Persistent Inventory

The persistent inventory is an mmap-backed graph in the `state` file. It models dump streams, media objects, and media files and survives interrupted sessions.

Important functions:

- `pi_allocdesc()` grows/remaps descriptor pages and maintains a free list.
- `pi_insertfile()` creates/updates stream/object/file descriptors, infers previous object ends, records IDs/labels, indexes, extent starting points, flags, and file sizes.
- `pi_addfile()` records data, inventory, and terminator media files. It also reads on-media inventory, optionally writes it into online inventory, and transcribes it.
- `pi_transcribe()` converts online/on-media `inv_session_t` to the persistent inventory graph.
- `pi_checkpoint()` records the current drive mark and next extent group for resume.
- `pi_neededobjs_dir_alloc()` and `pi_neededobjs_nondir_alloc()` compute which media objects are still needed.
- `pi_alldone()` uses needed-object calculation to determine restore completion.
- `pi_hiteod()`, `pi_hiteom()`, and `pi_hitnextdump()` mark known stream/object ends.
- `pi_know_no_more_on_object()` and `pi_know_no_more_beyond_on_object()` let media traversal avoid useless scans.
- `pi_show_nomloglock()` renders a detailed inventory status.

The inventory is guarded by `pi_lock()`/`pi_unlock()` around shared mutation and scanning.

## Partial File Registry

The `persp->a.parrest` registry tracks byte spans restored by each stream for split regular files.

- `partial_reg()` records incomplete restored byte ranges per inode and stream.
- `partial_check()` returns true when no partial record exists or when all spans now cover the file.
- `partial_check2()` merges unordered stream byte spans by repeatedly extending the covered prefix until EOF or a gap.

This prevents early application of DMAPI xattrs and post-data XFS inode flags when one file is split across streams.

## Completion and Cleanup

`finalize()`:

- Restores delayed directory attributes through `tree_setattr()`.
- Removes orphanage if empty through `tree_delorph()`.
- Deletes persistent inomap.
- For cumulative restore, increments dump count, records last dump ID/label, and invalidates only session state.
- For non-cumulative restore, invalidates accumulated state so `content_complete()` removes housekeeping.

`content_complete()` reports complete/interrupted status, quota-file hints, elapsed time, persists accumulated elapsed time, and wipes housekeeping when appropriate.

`wipepersstate()` removes all entries in the housekeeping directory and then removes the directory itself.

## Compatibility and Overwrite Policy

- `dumpcompat()` ensures cumulative restore begins with a non-resumed level 0 dump and subsequent dumps are based on the last applied dump.
- `askinvforbaseof()` queries inventory for the relevant base session.
- `content_overwrite_ok()` enforces overwrite inhibition, newer-than policy, and changed-file policy by inspecting `lstat()` results and saved ctime/mtime.

## Error Handling Notes

- Drive errors are mapped into `rv_t` values such as `RV_EOD`, `RV_CORRUPT`, `RV_DRIVE`, and `RV_CORE`.
- Most file creation/metadata failures are warnings and continue restore, discarding or partially restoring that file.
- Media corruption can trigger resync with `do_next_mark()`.
- Assertions are used heavily for persistent-state invariants, descriptor bounds, expected sizes, and impossible media states.
- Several restore phases are resumable through persistent flags, so interrupted sessions skip completed steps.

## Cross-File Relationships

- Uses `dirattr.c` to store directory attributes and directory xattrs during directory pass, then restore them later.
- Uses `tree` for path/link discovery, subtree selection, directory materialization, dir attributes, and orphan handling.
- Uses `inomap` to decide which non-directory inodes still need restore.
- Uses `namreg` for persisted directory entry names.
- Uses inventory APIs to validate and transcribe dump media inventories.
