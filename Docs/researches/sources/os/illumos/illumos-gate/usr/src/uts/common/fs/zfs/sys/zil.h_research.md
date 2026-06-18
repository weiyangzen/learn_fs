# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil.h

Defines the ZFS Intent Log public/on-disk record format, transaction type constants, log record structures, write-state categories, parser/replay callbacks, and ZIL lifecycle APIs.

Key elements:
- `zil_header_t` stores claim/replay sequencing, log chain block pointer, flags, and padding.
- `zil_chain_t` describes log block chaining and trailer checksum placement.
- Transaction types cover create, mkdir, xattr mkdir, symlink, remove, rmdir, link, rename, write, truncate, setattr, ACL formats, create/mkdir variants with ACL/attrs, and write2.
- `TX_CI` marks case-insensitive operation variants.
- `TX_OOO()` identifies record types that can be logged out of order.
- `lr_t` is the common log record header; specific `lr_*` structs define create, ACL create, remove, link, rename, write, truncate, setattr, and ACL records.
- `itx_t` is the in-memory intent transaction wrapper.

Main dependencies and interactions:
- Depends on SPA, ZIO, DMU, and ZIO crypto.
- Used by ZPL logging in `zfs_znode.h` and ZIL internals in `zil_impl.h`.
- Exposes parse, replay, claim, sync, suspend/resume, commit, destroy, and LWB block tracking APIs.

Implementation notes:
- Many structures are on-disk ABI and must stay cross-architecture aligned.
- Large dnode slot count is packed into high object-ID bits for log record compatibility.
- Write logging has three states: indirect block pointer, copied immediate data, or deferred copy.
