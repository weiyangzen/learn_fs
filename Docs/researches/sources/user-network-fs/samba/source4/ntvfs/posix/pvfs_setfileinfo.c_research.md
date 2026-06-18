# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_setfileinfo.c

Purpose: `pvfs_setfileinfo.c` implements metadata updates by open handle and by pathname. It handles timestamps, DOS attributes, EAs, delete-on-close, allocation and EOF size changes, position/mode, stream and file renames, and security descriptor writes.

Important APIs, types, and functions: Public functions are `pvfs_setfileinfo_ea_set`, `pvfs_setfileinfo`, and `pvfs_setpathinfo`. Key helpers are `pvfs_setfileinfo_access`, `pvfs_setfileinfo_rename_stream`, `pvfs_setfileinfo_rename`, `pvfs_retry_setpathinfo`, and `pvfs_setpathinfo_setup_retry`.

Control flow: Both set-by-handle and set-by-path compute required access from the information level, refresh or resolve current file state, copy current `pvfs_filename` data into `newstats`, and update fields according to the level. EA levels update xattr-backed DOS EAs immediately. Delete disposition delegates to `pvfs_set_delete_on_close`. Allocation/EOF changes break level-II oplocks and truncate POSIX files or stream blobs. Rename levels delegate to the shared rename helper and update open-db path state. Security descriptor updates notify and call the ACL backend. After field changes, the code applies size changes, `utimes`, open-db write-time updates, chmod/fchmod for DOS attributes, notify events, and `pvfs_dosattrib_save`.

State and persistence behavior: It persists DOS attributes, EA size, create/change times, allocation size, and stream metadata in xattrs/EADB; POSIX size changes use `truncate`/`ftruncate`; timestamps use `utimes`; mode changes use PVFS syscall wrappers. Open-handle write-time timers are canceled or forced when an explicit write time is set.

Dependencies and integration points: It integrates with access checks, path resolution, open-db share/oplock checks, async retry, stream helpers, xattr DOS EA storage, ACL backends, notify, chmod wrappers, and `pvfs_open.c` delete-on-close logic.

Risks: Setpathinfo and setfileinfo differ subtly for access, open-db checks, ignored levels, and allocation-size increase handling. Size updates must coordinate with oplocks and share modes. A missing `talloc_free(lck)` in some error paths would be easy to introduce around retries. Rename semantics differ by SMB1 and SMB2.

Test signals: Cover every set info level, explicit and delayed write times, allocation versus EOF truncation, path-level sharing retry, stream truncation, EA add/update/delete via zero-length values, delete-on-close rules, SMB2 rename paths, ACL writes, and notify masks.
