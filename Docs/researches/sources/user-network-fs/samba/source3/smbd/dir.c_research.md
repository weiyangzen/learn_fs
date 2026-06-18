# sources/user-network-fs/samba/source3/smbd/dir.c

## Purpose
`dir.c` implements smbd directory handles and directory search pointers. It opens directory FSPs, allocates SMB1 directory pointer IDs, reads and filters entries, performs access-based visibility checks, tracks opens below a directory, and verifies whether directories can be deleted.

## Important APIs, types, and functions
- `struct smb_Dir` wraps a VFS `DIR *`, directory `smb_filename`, file-number offset, case-sensitivity state, and back pointer to the owning FSP.
- `struct dptr_struct` stores SMB search handle state: dnum, wildcard, attributes, wildcard/stat optimization flags, privilege flag, overflow entry, and resume name.
- `init_dptrs()`, `dptr_create()`, `dptr_CloseDir()`, `dptr_closecnum()`, and dptr accessors manage SMB1/SMB2 directory pointer state.
- `dptr_ReadDirName()` optimizes non-wildcard searches by `fstatat()` and falls back to scanning for mangled or case-insensitive matches.
- `smbd_dirptr_get_entry()` is the main entry enumeration/filtering loop.
- `OpenDir()`, `OpenDir_from_pathref()`, `ReadDirName()`, and `RewindDir()` expose lower-level directory handles.
- `is_visible_fsp()`, `have_file_open_below()`, `opens_below_forall[_read]()`, and `can_delete_directory_hnd()/fsp()` implement visibility and delete checks.

## Control flow
Directory searches begin by checking `SEC_DIR_LIST`, opening a directory handle from an FSP, allocating an SMB1 dnum if needed, and storing wildcard/attribute matching state. Enumeration returns `.` and `..` first, then VFS names. It skips veto paths, stale smbd temporary names, invisible files, DFS/symlink cases that should be hidden, and entries whose DOS mode does not match requested attributes. For non-wildcard queries, Samba avoids scanning where possible by using `FSTATAT`, then scans only for mangled-name or case-insensitive fallback.

Visibility is option-driven: `hide unreadable`, `hide unwriteable files`, `hide special files`, and `hide new files timeout` can suppress entries after approximate ACL/write/special-file checks. Directory deletion scans entries, optionally ignores veto/invisible entries when `delete veto files = yes`, treats DFS links as non-empty, handles dangling symlinks specially, and finally denies deletion if share-mode records or local FSPs show open files below the directory.

## State and persistence behavior
Directory search state is in-memory under `sconn->searches` and per-FSP `dptr`. The VFS directory fd is closed by `smb_Dir_destructor()`, which also invalidates the FSP fd. `ReadDirName()` can persistently unlink stale smbd temporary names as root. Delete-check helpers read share-mode databases but do not update them.

## Dependencies and integration points
This file depends on VFS directory/open/stat/unlink APIs, bitmap allocation, name mangling, DFS/reparse helpers, ACL/security checks, DOS mode mapping from `dosmode.c`, close helpers from `close.c`, share-mode traversal, and loadparm visibility/delete settings. SMB1 trans2/search and SMB2 query-directory code use the exported dptr APIs.

## Risks and edge cases
- Search handle numbering is biased by one and has separate old-SMB 1-255 versus new 256+ ranges.
- `dptr_closecnum()` closes files while iterating directory pointers, so it copies the FSP pointer before close invalidates dptr memory.
- Visibility checks are intentionally approximate and must not be treated as authorization.
- Symlink, DFS, POSIX path, and case-insensitive fallback behavior is subtle and protocol/configuration dependent.
- Open-below checks are path-prefix based and race with renames/connectpath changes.

## Test signals
Tests should cover old/new dptr allocation limits, wildcard and non-wildcard query behavior, mangled and case-insensitive lookup fallback, veto/invisible/hidden-new-file filtering, DFS symlink masquerading, POSIX symlink visibility, stale temp-name cleanup, directory delete with veto files, and strict rename/open-below checks.
