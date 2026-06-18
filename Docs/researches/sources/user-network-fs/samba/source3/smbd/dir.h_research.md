# sources/user-network-fs/samba/source3/smbd/dir.h

## Purpose
`dir.h` declares the public directory-handle, directory-pointer, visibility, open-below traversal, and delete-check interfaces implemented by `dir.c`.

## Important APIs, types, and functions
The header forward-declares opaque `struct smb_Dir` and `struct dptr_struct`, then exports `OpenDir()`, `OpenDir_from_pathref()`, `ReadDirName()`, `RewindDir()`, dptr lifecycle/accessor functions, `smbd_dirptr_get_entry()`, overflow/resume helpers, `is_visible_fsp()`, `have_file_open_below()`, `opens_below_forall[_read]()`, and `can_delete_directory_hnd()/fsp()`.

## Control flow
Consumers use this header to create directory handles from paths or pathref FSPs, attach search state to SMB request processing, enumerate filtered directory entries, preserve one overflow entry when a response buffer fills, and ask whether a directory is deletable before setting delete-on-close or completing rmdir.

## State and persistence behavior
The header itself has no state. It intentionally hides the layout of `smb_Dir` and `dptr_struct` so ownership and fd cleanup remain centralized in `dir.c`.

## Dependencies and integration points
It depends on core smbd types from `includes.h` and is included by close/delete code, query-directory reply code, access checks, and other path traversal components.

## Risks and edge cases
- Callers must respect ownership conventions: returned names and `smb_filename` objects may be moved, and directory handles must be freed to close fds.
- `dptr_*` APIs are meaningful only for FSPs and server connections initialized with directory pointer bitmap state.
- `is_visible_fsp()` is not an authorization function.

## Test signals
Build coverage should catch prototype drift. Runtime tests are those for `dir.c`, especially public API use from close/rmdir and SMB query-directory paths.
