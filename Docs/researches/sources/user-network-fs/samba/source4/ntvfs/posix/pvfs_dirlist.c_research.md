# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_dirlist.c

Purpose: implements PVFS directory enumeration, wildcard matching, resume offsets, name-based seeks, and directory-empty checks.

Important APIs and types: `struct pvfs_dir` tracks open DIR handle, wildcard pattern, fake/real offsets, cached names, and end-of-search state. Public functions include `pvfs_list_start`, `pvfs_list_next`, `pvfs_list_unix_path`, `pvfs_list_eos`, `pvfs_list_seek`, `pvfs_list_seek_ofs`, and `pvfs_directory_empty`. `dcache_add` maintains a 100-entry resume cache.

Control flow: `pvfs_list_start` splits the resolved Unix path into directory plus pattern. Non-wildcard searches use `pvfs_list_no_wildcard` and avoid `opendir`; wildcard searches open the directory, initialize fake offsets for `.` and `..`, and allocate the cache. `pvfs_list_next` returns dot entries first if they match, then scans `readdir`, skipping dot entries, matching long names or generated short names, and maps `telldir` offsets by adding `DIR_OFFSET_BASE`. Seek operations first consult special dot offsets and the cache, then rescan from the start.

State and persistence: state is per-search and talloc-scoped; the destructor closes `DIR *`. No persistent state is written.

Dependencies and integration points: uses PVFS name resolution output, `ms_fnmatch_protocol`, short-name generation, POSIX directory APIs, and protocol selection from the NTVFS context.

Risks: resume offsets are inherently OS-dependent, so fake base constants avoid collisions with observed end-of-directory values; non-wildcard path handling mutates `name->full_name` at the final slash; short-name matching adds cost. Test signals include wildcard/no-wildcard enumeration, dot ordering, protocol-specific matching, resume by name and offset, cache wraparound, empty-directory behavior, and platforms with unusual `telldir` values.
