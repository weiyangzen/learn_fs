# sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.h

Purpose: declares the POSIX EADB interface by forward-declaring `struct pvfs_state` and including the generated `posix_eadb_proto.h` prototypes.

Important APIs and types: the header itself defines no functions beyond including generated prototypes. The important surface is the raw TDB-backed xattr API and, when file-server support is enabled, the `pvfs_state` wrapper API implemented in `posix_eadb.c`.

Control flow: consumers include this header to call EADB routines without needing the full `vfs_posix.h` definition at declaration time. The generated prototype header supplies signatures for pull, push, delete, unlink, and list routines.

State and persistence: no state is stored here. Persistence is in the TDB database managed by the implementation.

Dependencies and integration points: bridges POSIX NTVFS code and generated prototype infrastructure under `source4/ntvfs/posix`. The forward declaration reduces include coupling.

Risks: correctness depends on generated prototypes matching implementation signatures and compile flags such as `WITH_NTVFS_FILESERVER`. Test signals are compile-time: include this header from translation units with and without full `pvfs_state` definition and verify no signature drift.
