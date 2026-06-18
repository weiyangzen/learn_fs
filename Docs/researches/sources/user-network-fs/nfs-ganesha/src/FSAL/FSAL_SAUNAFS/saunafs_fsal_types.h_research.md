# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs_fsal_types.h

Purpose: this header defines FSAL_SAUNAFS private module, export, handle, state, pNFS, and constant types used by the SaunaFS backend.

Important types and constants: `SAUNAFS_VERSION` and `kDisconnectedChunkServerVersion` encode chunkserver version semantics. Block/chunk constants define a 64 KiB block, 1024 blocks per chunk, and `SFSCHUNKSIZE`. Special inode bounds separate regular inodes from synthetic inodes. `SAUNAFS_SUPPORTED_ATTRS` advertises POSIX-like attributes plus ACL and NFSv4 xattr support. `struct SaunaFSModule` embeds `fsal_module`, object operations, and static fsinfo. `struct SaunaFSExport` embeds `fsal_export`, root handle, `sau_t *fsInstance`, init params, fileinfo cache, pNFS mode flags, and cache limits. `struct SaunaFSFd`, `struct SaunaFSStateFd`, `struct SaunaFSHandleKey`, `struct SaunaFSHandle`, `struct DSWire`, and `struct DataServerHandle` define open state, handle identity, share reservation, and pNFS data-server handles.

Control flow and state: handles carry both public `fsal_obj_handle` state and SaunaFS-specific inode/export/share/fd state. Exports own the SaunaFS client instance and cache. NFSv4 state objects embed a `SaunaFSFd` so opens/locks can associate a client-library fileinfo with protocol state. pNFS data-server handles track an inode and optional cache entry.

Dependencies and integration points: includes `fsal_api.h`, `fileinfo_cache.h`, and the SaunaFS C API. Other FSAL_SAUNAFS files use these structures for export creation, handle allocation, IO, ACL, and pNFS layout operations.

Risks: handle keys contain module id, export id, and inode, so export id stability is part of persistent handle identity. Cache settings and pNFS flags are per-export mutable runtime behavior. The file exposes constants that must remain consistent with SaunaFS server/client chunk sizing and inode reservation rules.

Test signals: construct exports with cache and pNFS options, validate handle key encoding/decoding across export ids, assert `SAUNAFS_SUPPORTED_ATTRS` matches implemented ops, and test fileinfo cache cleanup through export and state destruction.
