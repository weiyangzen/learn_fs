# sources/user-network-fs/samba/source4/ntvfs/simple/svfs.h

Purpose: `svfs.h` defines private structs for the simple NTVFS backend, a deliberately minimal disk backend used for basic file serving and tests.

Important APIs, types, and functions: It defines `svfs_private`, `svfs_dir`, nested `svfs_dirfile`, `svfs_file`, and `search_state`. These track connection path, open files, directory listings, and search handles.

Control flow: The header has no executable flow. `vfs_simple.c` allocates `svfs_private` on tree connect, adds/removes `svfs_file` nodes as files open and close, and creates `search_state` entries for TRANS2 directory searches.

State and persistence behavior: Runtime state is per-tree-connect and in memory: base path, next search handle, open file list, and open search list. Persistent state is only the underlying filesystem files accessed by fd/path.

Dependencies and integration points: It is consumed by `vfs_simple.c` and `svfs_util.c` and relies on NTVFS handles, `struct stat`, and Samba dlinklist conventions.

Risks: The structures are intentionally sparse and lack locking, share mode, ACL, xattr, oplock, and full metadata state. Search handles are simple 16-bit counters and can wrap on long-lived sessions.

Test signals: Simple backend tests should cover open/close list maintenance, search state lifecycle, directory listing allocation, and behavior when unsupported SMB features are requested.
