# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_internal.h

Purpose: this header declares shared FSAL_SAUNAFS internal functions for contexts, export/object operation vector initialization, handle allocation, ACL operations, error conversion, and pNFS operation setup.

Important APIs: `createContext`, `exportOperationsInit`, `handleOperationsInit`, `allocateHandle`, `deleteHandle`, `getACL`, `setACL`, `saunafsToFsalError`, `fsalLastError`, `nfs4LastError`, `pnfsMdsOperationsInit`, `exportOperationsPnfs`, `pnfsDsOperationsInit`, and `handleOperationsPnfs`.

Control flow and state: this header ties independent implementation files into the module registration path. Handles allocated by `allocateHandle` must be released through `deleteHandle`. ACL helpers consume `SaunaFSExport`, inode ids, mode, and FSAL ACL references. Error helpers centralize C API status mapping.

Dependencies and integration points: includes local FSAL filesystem support and `saunafs_fsal_types.h`, making the private SaunaFS structures visible to all implementation files.

Risks: broad internal declarations mean operation initialization, pNFS hooks, and handle lifetime must remain ABI-consistent across multiple compilation units. Any signature drift can silently break module registration or object op vectors.

Test signals: build-time coverage is primary; runtime smoke tests should create an export, allocate/release handles, invoke ACL helpers, and verify pNFS operation vectors are populated only when enabled.
