# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.h

This header defines the public and internal structures for File Handle Affinity.

Key contents:
- Default controls: enable FHA, 4 MiB bin shift, up to 8 nfsd threads per file handle, and unlimited requests per nfsd by default.
- Defines `FHA_HASH_SIZE` as 251.
- Defines `struct fha_ctls`, `struct fha_hash_entry`, `struct fha_hash_slot`, `struct fha_info`, `struct fha_callbacks`, and `struct fha_params`.
- Callback table abstracts NFS operation decoding: proc mapping, mbuf realignment, file-handle extraction, read/write detection, offset extraction, no-offset checks, lock-type selection, and stats sysctl handling.
- Declares `fha_init()`, `fha_uninit()`, `fha_assign()`, `fha_nd_complete()`, and `fhe_stats_sysctl()`.

Important dependencies:
- Only active under `_KERNEL`.
- Relies on RPC service thread/list types and mutex/list primitives.

Risks and notes:
- The header intentionally keeps the scheduler independent of exact NFSv2/v3 wire parsing by requiring callbacks.
