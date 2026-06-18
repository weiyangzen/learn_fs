# File Research: sources/os/linux/linux/fs/smb/client/readdir.c

## Purpose
Implements CIFS/SMB directory enumeration, FIND_FIRST/FIND_NEXT search state management, directory entry parsing across SMB info levels, dcache priming, cached directory entry serving, and VFS `iterate_shared`-style emission through `cifs_readdir()`.

## Main Interfaces
- Directory read entry point: `cifs_readdir()`.
- Search setup: `initiate_cifs_search()` and `_initiate_cifs_search()`.
- Search positioning: `find_cifs_entry()`, `nxt_dir_entry()`, `cifs_save_resume_key()`.
- Entry conversion: `cifs_fill_dirent()`, `cifs_dir_info_to_fattr()`, POSIX/Unix/full/std info converters.
- Dcache/cache helpers: `cifs_prime_dcache()`, `cifs_dir_emit()`, cached dirent add/emit/count helpers.

## Control Flow
`cifs_readdir()` builds the directory path, tries to open and serve a cached directory, emits dot entries, initiates a network search if needed, seeks to the requested logical position, fetches more buffers with `query_dir_next()` as needed, converts each returned record to a VFS name and `cifs_fattr`, primes the dcache, emits to the VFS dir context, and optionally stores entries in the cached-dir structure.

Search setup chooses the info level based on legacy Unix extensions, SMB3 POSIX extensions, NT find capability, and server inode mount options. If server inode support fails with `-EOPNOTSUPP`, it disables server inode use and retries.

## State And Synchronization
Per-open directory state lives in `struct cifsFileInfo` and its `srch_inf`, including the network buffer, last entry, resume key/name, index of last entry, entries-in-buffer, unicode flag, empty/end-of-search flags, and invalid handle state. Cached directory entries are protected by `cfid->dirents.de_mutex` and accounted per tcon and globally with atomic counters.

## Integration Points
Calls dialect `query_dir_first`, `query_dir_next`, `close_dir`, `dir_needs_close`, and `calc_smb_size` callbacks. Uses inode conversion helpers from `inode.c`, reparse parsing, idmap/ACL helpers, cached-dir open/close APIs, and VFS `dir_emit()`/dcache aliasing APIs.

## Notable Behaviors
- Suppresses server-returned `.` and `..` because VFS dot entries are emitted first.
- Validates next-entry offsets and entry bounds against the SMB buffer end.
- Rewinds and restarts search when the caller seeks backward or cached directory metadata indicates change.
- Marks ACL-derived, MF symlink, SFU, reparse, symlink, block, and char entries for later revalidation when readdir metadata is insufficient.
- Auto-disables server inode numbers when directory entries lack usable inode IDs.

## Risks And Review Focus
- Directory parsing is buffer-boundary sensitive across many SMB info levels.
- Cached directory serving must preserve `ctx->pos` holes caused by suppressed dot entries.
- Dcache priming must avoid clobbering mounted dentries and must handle inode type/uniqueid changes.
- Search rewind and network-buffer cleanup must avoid stale pointers in `srch_inf`.
