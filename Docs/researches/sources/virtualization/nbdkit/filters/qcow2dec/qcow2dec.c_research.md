# File Research: sources/virtualization/nbdkit/filters/qcow2dec/qcow2dec.c

This filter exposes a qcow2 file provided by the underlying plugin as a read-only virtual disk. It advertises no write support, emulated cache support, multi-conn consistency, and extents support. `dump_plugin` reports deflate and zstd support according to build-time compression libraries.

`.prepare` is serialized by a global mutex and loads qcow2 metadata once. `get_qcow2_metadata` validates the backend file size, reads and byte-swaps the qcow2 header, checks magic/version, rejects backing files, encryption, snapshots, unsupported incompatible features, invalid cluster sizes, and oversized or out-of-bounds L1 tables. Version 2 files get default v3-like fields. The L1 table is loaded and byte-swapped; L2 table descriptors are allocated lazily, one mutex per L1 entry.

Reads are cluster-based. `qcow2dec_pread` handles unaligned heads/tails through a temporary cluster buffer and aligned bodies directly. `read_l2_entry` maps virtual offsets through L1/L2 indexes, validates reserved bits and L2 table offsets, lazily reads and byte-swaps L2 table clusters under per-table locks, and returns unallocated state. `read_cluster` returns zeroes for missing/zero clusters, reads ordinary allocated clusters from the qcow2 file, or dispatches compressed clusters.

Compressed cluster handling decodes qcow2 compressed L2 fields into host file offset and sector count, bounds-checks reads, caps compressed allocation to twice the cluster size, and decompresses with raw deflate or zstd when available. Unsupported compression libraries are reported once through static atomic flags.

`qcow2dec_extents` rounds the query to cluster boundaries and emits hole/zero extents for unallocated or explicit-zero clusters, allocated extents for compressed and ordinary data clusters, and honors `REQ_ONE`. Major limitations are explicit and enforced: no backing files, no encryption, no internal snapshots, no external data files or extended L2, and no metadata refresh if the qcow2 file size changes after preparation.
