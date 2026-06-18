# File Research: sources/os/linux/linux-stable/fs/smb/client/readdir.c

Read status: complete.

## Purpose

Implements CIFS/SMB directory enumeration, find-first/find-next search state, directory-entry metadata conversion, dcache priming, resume positioning, and cached directory entry emission.

## Main Responsibilities

- Start and continue directory searches at the right SMB information level for Unix extensions, SMB3 POSIX extensions, legacy standard info, server inode mode, or full directory info.
- Convert directory search entries into Linux names, inode numbers, dtypes, and `cifs_fattr`.
- Skip `.` and `..` entries returned by servers after VFS dot emission.
- Maintain resume keys/names for find-next operations.
- Restart directory searches when seeking backward or when directory metadata changed.
- Prime the dcache from readdir results when safe.
- Support cached directory handles and cached dirent replay.
- Mark entries needing full revalidation when readdir data is incomplete for ACLs, reparse points, MF symlinks, or special files.

## Important Functions

- `cifs_prime_dcache()`
  - Looks up or allocates child dentries from readdir results.
  - Updates matching inodes in place when unique id and type are stable.
  - Avoids priming entries that immediately need revalidation.
  - Handles reparse-point metadata carefully to avoid clobbering known symlink/device/ownership data with incomplete query-dir data.

- `cifs_fill_common_info()`
  - Applies mount uid/gid, directory/file mode defaults, dtype, readonly masking, unknown-nlink marking, ACL revalidation flags, SFU FIFO handling, and reparse-point conversion.

- `cifs_posix_to_fattr()`
  - Converts `SMB_FIND_FILE_POSIX_INFO` entries to `cifs_fattr`.
  - Parses POSIX owner/group SIDs, mode, inode, size, allocation, nlink, DOS attrs, reparse tag, and special-file revalidation needs.

- `cifs_dir_info_to_fattr()` / `cifs_fulldir_info_to_fattr()` / `cifs_std_info_to_fattr()`
  - Convert the different SMB directory info response formats into common `cifs_fattr`.

- `_initiate_cifs_search()` / `initiate_cifs_search()`
  - Allocate `struct cifsFileInfo` for directory state when needed.
  - Choose info level and search flags.
  - Call `server->ops->query_dir_first`.
  - Retry briefly on `-EDEADLK` credit shortage and disable `serverino` if unsupported.

- `cifs_unicode_bytelen()` / `nxt_dir_entry()`
  - Determine Unicode filename byte length and advance between variable-sized search entries with bounds checks.

- `cifs_fill_dirent*()` / `cifs_fill_dirent()`
  - Extract name pointer, name length, resume key, and inode number from each supported directory info format.

- `cifs_entry_is_dot()`
  - Detects `.` and `..` in Unicode or byte names.

- `is_dir_changed()` / `cifs_save_resume_key()`
  - Detect directory invalidation and store resume state from the current entry.

- `find_cifs_entry()`
  - Locates the directory entry corresponding to `ctx->pos`.
  - Rewinds and restarts searches when necessary, issues find-next calls until the target buffer is reached, and scans within the current SMB response.

- `emit_cached_dirents()` / `add_cached_dirent()` / `cifs_dir_emit()`
  - Replay or populate cached dirent lists for cached directory handles.
  - Track entry count and byte accounting per tcon and globally.

- `cifs_filldir()`
  - Converts a single network entry to a VFS dirent.
  - Handles UTF-16 conversion, fattr conversion, inode-number selection, MF symlink revalidation marking, dcache priming, and dirent emission.

- `cifs_readdir()`
  - Main VFS readdir implementation.
  - Builds path, attempts cached directory replay, starts search when needed, emits dots, finds current entry, opens cache for population, loops through entries, updates `ctx->pos`, resume key, and cache accounting.

## Dependencies

- Uses CIFS search state in `struct cifsFileInfo`, dialect `query_dir_first/query_dir_next/close_dir/calc_smb_size` operations, cached directory subsystem, inode/fattr helpers from `inode.c`, SID-to-id and POSIX info parsing helpers, Unicode conversion, reparse helpers, and VFS `dir_context`.

## Notable Behaviors

- Readdir deliberately marks some entries for later stat revalidation because query-dir responses do not carry enough ACL, special-file, symlink, or reparse detail.
- Dot entries from the server are suppressed because VFS emits dots first.
- Search buffer traversal has explicit overflow and end-of-SMB checks.
- Cached dirents preserve original logical positions so lseek/readdir replay can maintain expected `ctx->pos` behavior even when skipped dot entries create holes.
- If a returned inode number is absent while `serverino` is requested, the code generates one and may autodisable server inode numbers.
