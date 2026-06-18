## sources/user-network-fs/nfs-utils/utils/nfsref/add.c

Purpose: Implements `nfsref add`, creating a local NFS basic junction and storing one or more fileset locations.

Important APIs/types/functions: `nfsref_add_help`, `nfsref_add_build_fsloc`, `nfsref_add_build_fsloc_list`, `nfsref_add_nfs_basic`, and `nfsref_add`. It populates `struct nfs_fsloc` defaults, converts POSIX export paths with `nsdb_posix_to_path_array`, and writes metadata with `nfs_add_junction`.

Control flow: Public `nfsref_add` ensures the junction path exists as a directory, selects the requested type, builds a linked list of server/export pairs, writes junction metadata, frees locations, and reports success/failure.

State and persistence: Persists referral metadata on the junction filesystem object through the junction support library. Default FSL fields encode conservative NFSv4 location behavior.

Dependencies and integration: Uses uuid headers, `junction.h`, `xlog`, and shared `nfsref.h`; called from `nfsref.c` after root/type/argument validation.

Risks and test signals: The list builder appends only through `result->nfl_next`, so more than two locations deserve tests. Also test odd argument counts, existing junction metadata, allocation failures, path conversion errors, and export-cache flush by the caller.
