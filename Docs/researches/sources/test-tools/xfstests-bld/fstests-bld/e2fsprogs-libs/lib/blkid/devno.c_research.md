# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devno.c

Purpose: maps a block device number (`dev_t`) back to a pathname by scanning device directories.

Important APIs and control flow: `blkid_strndup` and `blkid_strdup` provide local string duplication helpers. `blkid__scan_dir(dirname, devno, list, devname)` scans one directory, skipping dot entries and overlong paths, stats children, returns the first block device whose `st_rdev` matches, and optionally queues real subdirectories for breadth-first traversal. `blkid_devno_to_devname(devno)` seeds `/devices`, `/devfs`, and `/dev`, then performs breadth-first directory scanning until a matching path is found or all lists are exhausted.

State and persistence: uses transient `dir_list` queues and returns an allocated pathname owned by the caller. No persistent state.

Dependencies and integration: used by `devname.c` fallback resolution and DM mapper scanning. Depends on `stat`, `lstat`, directory APIs, and `makedev` configuration.

Risks and test signals: recursive scan can be expensive, follows `stat` for device checks, and uses fixed 1024-byte path buffer. Test matching device numbers, symlink directories, permission-denied directories, no-match behavior, and breadth-first preference.
