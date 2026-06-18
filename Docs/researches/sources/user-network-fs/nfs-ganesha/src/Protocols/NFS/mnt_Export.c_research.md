## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Export.c

Purpose: implements MOUNT `EXPORT`, returning exports visible to the caller.

APIs and flow: `mnt_Export` iterates all exports with `foreach_gsh_export`. `proc_export` sets each export in `op_ctx`, runs `export_check_access`, filters out inaccessible or non-NFSv3 exports, builds an `exportnode`, copies client group strings from export-specific clients or global export options under locks, selects pseudo or full path, and links nodes into the result list. `mnt_Export_Free` frees nested group nodes and path refstrings.

State/dependencies: reads export manager state, export permissions, client lists, and op context. Allocates response-owned linked lists.

Risks/tests: lock/ref ordering and cleanup are key. Test export visibility by client, pseudo vs path mode, empty client list fallback, memory cleanup, and concurrent export updates.
