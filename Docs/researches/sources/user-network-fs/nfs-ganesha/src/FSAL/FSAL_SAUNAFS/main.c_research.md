# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/main.c

This file registers and initializes the SaunaFS FSAL module, defines static capabilities and configuration parameters, creates exports, optionally enables pNFS MDS/DS support, creates the root handle, and unregisters the module on unload.

The singleton `SaunaFS` advertises POSIX-like capabilities: links, symlinks, locks, named attrs/xattrs, unique handles, pNFS MDS and DS support, optional ACL support, and SaunaFS attribute masks. Module-level config toggles static FS info such as umask, maxread/maxwrite, pNFS flags, tracing, and grace. Export config includes master hostname/port, mountpoint/subfolder, delayed init, read/write/cache timings, write-cache parameters, keep-cache, fileinfo cache limits, and password/md5 credentials. `createExport` parses config, initializes a `sau_t` client instance, attaches the export, creates DS registration when enabled, installs MDS export ops when enabled, reads root attributes, and allocates the root handle. `initializeSaunaFS` registers the FSAL, installs module ops, DS ops, MDS ops, and object ops.

State is process-local for the module and per-export for `SaunaFSExport`, including the `sau_t` instance, root handle, pNFS booleans, and optional fileinfo cache. Filesystem persistence lives in the SaunaFS cluster.

Dependencies include FSAL registration/config APIs, `pnfs_utils`, `context_wrap`, private SaunaFS types/internal helpers, `pnfs_ds_insert/remove/put`, and the SaunaFS C API.

Risks include complex pNFS DS registration cleanup, overwriting configured `subfolder` with `CTX_FULLPATH`, possible mismatch between FSAL config flags and actual export `fs_supports` results, and abort on unregister failure. Test signals should cover config parsing defaults, failed `sau_init_with_params`, pNFS MDS-only/DS-only/both/none exports, duplicate DS server id, root getattr failure cleanup, fileinfo cache creation failure, and module load/unload.
