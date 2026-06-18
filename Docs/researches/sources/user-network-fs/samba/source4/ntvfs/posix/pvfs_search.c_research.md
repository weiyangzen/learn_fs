# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_search.c

Purpose: `pvfs_search.c` implements directory enumeration for old SMB search, TRANS2 find-first/find-next, SMB2 find, and find-close operations. It converts directory entries into requested wire information levels while tracking resumable search state.

Important APIs, types, and functions: Public functions are `pvfs_search_first`, `pvfs_search_next`, and `pvfs_search_close`. Local helpers include `pvfs_search_destructor`, timer setup/cleanup functions, `fill_search_info`, `pvfs_search_fill`, old search handlers, trans2 handlers, and SMB2 handlers. State is `struct pvfs_search_state` plus `pvfs->search.idtree` and per-directory-handle `f->search` for SMB2.

Control flow: Search-first resolves a wildcard path, checks parent traverse/list access, starts a `pvfs_dir` listing, allocates a search state, and fills up to the requested count with `pvfs_search_fill`. Each entry is resolved with `pvfs_resolve_partial`, filtered by attributes, and mapped according to `enum smb_search_data_level`. Old SMB searches allocate small numeric handles in an idtree and age out forgotten entries. TRANS2 searches support resume keys, last-name seeks, close flags, and EA-name lists. SMB2 searches require an open directory handle, validate pattern syntax, restart or single-entry flags, and store state on the directory `pvfs_file`.

State and persistence behavior: Search state is in memory only. Old and TRANS2 searches are stored in `pvfs->search.list`/idtree and guarded by inactivity timers; SMB2 state is owned by the directory handle. Directory entry metadata is read from POSIX stat and xattr/EADB DOS metadata at fill time.

Dependencies and integration points: It depends on name resolution, directory listing helpers, access checks, EA queries, short-name mangling, idtree, tevent timers, and ntvfs search callbacks that serialize results.

Risks: Resume offsets are truncated to 32 bits in result fields and rely on `pvfs_list_seek_ofs` to cope. Old clients often forget close requests, so cleanup policy matters. Returning zero results maps to different status values by protocol. SMB2 searches destroy previous handle search state on new search-first.

Test signals: Cover old SMB search handles/cookies, TRANS2 resume by name/key, close-if-end flags, SMB2 restart/single flags, attribute and must-attribute filters, EA-list levels, short-name fields, no-match statuses, and timer cleanup of leaked searches.
