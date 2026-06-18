# File Research: sources/virtualization/qemu/block/qcow2.h

## Role

This header defines qcow2 on-disk structures, format constants, feature bits, in-memory driver state, inline mapping helpers, and cross-module function prototypes for QEMU's qcow2 block driver.

It is shared by the implementation files for qcow2 core, refcounts, clusters, snapshots, caches, bitmaps, crypto, and compression.

## Format Constants

Important top-level limits and format values include:

- `QCOW_MAGIC` for the qcow/qcow2 file magic.
- Encryption method constants: none, legacy AES, and LUKS.
- Limits for crypt clusters, snapshots, cluster offsets, refcount table size, L1 table size, snapshot table size, bitmap count, and bitmap directory size.
- Worker limit `QCOW2_MAX_WORKERS`.
- L2 entry flags: copied, compressed, zero.
- Extended L2 subcluster count: `QCOW_EXTL2_SUBCLUSTERS_PER_CLUSTER` equals 32.
- Extended L2 allocation and zero bitmap macros for subcluster ranges.
- Normal and extended L2 entry sizes, L1 entry size, and reftable entry size.
- Cluster-bit range from 9 to 21, so clusters are 512 bytes through 2 MiB.
- Default cluster/cache sizes and Linux-specific cache clean interval.
- Driver option string constants for data files, lazy refcounts, discard policy, overlap checks, and cache sizing.

## On-Disk Structures

`QCowHeader` models the qcow2 file header. It contains v2 fields for magic, version, backing file location, cluster size, virtual size, encryption method, L1/refcount/snapshot tables, and v3 fields for incompatible/compatible/autoclear features, refcount order, header length, and compression type. The header is packed and compile-time checked for 8-byte alignment.

`QCowSnapshotHeader` is the packed on-disk snapshot entry header. `QCowSnapshotExtraData` stores newer snapshot metadata such as large VM-state size, disk size, and icount.

`Qcow2CryptoHeaderExtension`, `Qcow2UnknownHeaderExtension`, and `Qcow2BitmapHeaderExt` describe header extensions handled by `qcow2.c` and bitmap code.

## In-Memory Snapshot And State

`QCowSnapshot` is the in-memory representation of an internal snapshot, with L1 location/size, ID/name, disk size, VM-state size, timestamps, VM clock, icount, and unknown extra data preservation.

`BDRVQcow2State` is the central per-node state. It stores:

- cluster, subcluster, L2, L1, and refcount geometry
- active L1 table and offset
- L2 and refcount block caches
- cache-clean timer coroutine state
- in-flight cluster allocations
- refcount table, allocator cursors, refcount callbacks, and refcount limits
- coroutine lock
- crypto header/options/context and encryption tweak policy
- snapshot metadata
- persistent bitmap directory metadata
- qcow version, flags, lazy refcount mode, discard policy, overlap policy, and corruption signaling
- feature bitfields
- unknown header fields/extensions
- pending discard regions and cache discard policy
- stored image backing/data-file names and formats
- worker queue/thread counters
- external data-file child
- metadata preallocation detection cache
- compression type

This struct is the shared state all qcow2 modules operate on.

## Allocation Metadata

`Qcow2COWRegion` describes COW bytes before or after a guest write inside allocated clusters.

`QCowL2Meta` represents an in-flight write allocation requiring an L2 update. It tracks guest offset, allocated host offset, cluster count, whether old clusters should be kept, dependent request waiters, COW regions, COW skip/preallocation flags, optional original guest data vector for merged COW writes, linked metadata for the same request, and a list node for globally in-flight allocations.

This is the key handoff structure between allocation, data I/O, and final L2-linking.

## Cluster And Subcluster Types

`QCow2ClusterType` classifies whole clusters as unallocated, plain zero, allocated zero, normal, or compressed.

`QCow2SubclusterType` refines this for extended L2 images, distinguishing unallocated/plain, unallocated within allocated cluster, zero/plain, zero/allocated, normal, compressed, and invalid.

The header documents how standard L2 entries map directly to one subcluster, while extended L2 entries may mix subcluster states inside a normal or unallocated cluster. Invalid extended L2 bitmaps are detected when allocation and zero bits conflict.

## Feature Bits

Incompatible features include:

- dirty bit
- corrupt bit
- external data file
- compression type
- extended L2 entries

Compatible feature currently includes lazy refcounts.

Autoclear features include persistent bitmaps and raw external data-file mode.

The masks `QCOW2_INCOMPAT_MASK`, `QCOW2_COMPAT_FEAT_MASK`, and `QCOW2_AUTOCLEAR_MASK` define what this implementation understands.

## Metadata Overlap Checking

`QCow2MetadataOverlap` enumerates protected metadata regions:

- main header
- active L1
- active L2
- refcount table
- refcount block
- snapshot table
- inactive L1
- inactive L2
- bitmap directory

`QCOW2_OL_CONSTANT`, `QCOW2_OL_CACHED`, and `QCOW2_OL_ALL` define progressively broader overlap-check templates. These feed runtime overlap-check options in `qcow2.c`.

## Inline Helpers

The header provides compact helpers for:

- detecting extended L2/subcluster mode
- computing L2 entry size
- getting/setting L2 entries and extended L2 bitmaps with endian conversion
- checking external data-file use and raw-data-file flag
- cluster/subcluster alignment and offsets
- converting sizes to clusters, subclusters, and L1 entries
- deriving L1/L2/subcluster indices from guest offsets
- computing VM-state offset
- classifying an L2 entry as a cluster type
- classifying a specific subcluster from an L2 entry and bitmap
- checking whether a cluster type is allocated
- checking whether accurate refcounts are required
- computing COW-region guest boundaries
- computing absolute refcount deltas
- deriving refcount table index from host offset

The classification helpers encode important external data-file semantics: host offset zero can be a valid normal cluster when the copied flag disambiguates it.

## Cross-Module API Surface

The prototypes expose the qcow2 internal module boundary:

- Core: metadata size calculation, dirty/corrupt/header update, corruption signaling, table validation.
- Refcount: initialization/close, refcount get/update, allocation/free, discard processing, overlap checks, refcount checking/repair, refcount-order change, refcount table shrink, last-cluster detection, metadata preallocation detection.
- Cluster mapping: L1 grow/shrink/write, encryption, host-offset lookup, allocation, compressed cluster allocation/parsing, L2 linking/abort, discard, zeroize, dependency wait, zero-cluster expansion.
- Snapshots: create/goto/delete/list/load, read/write/free/check/fix snapshot tables.
- Cache: create/destroy, dirty marking, flush/write, dependency management, clean unused, empty, get/get-empty/put/is-offset/discard.
- Bitmaps: refcount checking, loading/storing persistent dirty bitmaps, bitmap info listing, reopen read/write transitions, truncate checks, create/remove capability, size calculation.
- Compression/encryption helpers: coroutine compression/decompression and encrypt/decrypt entry points.

## Design Notes

The header keeps qcow2 format details centralized so the implementation modules share one source of truth for feature flags, geometry, and metadata interpretation. It also makes the split between whole-cluster and subcluster state explicit, which is critical for extended L2 images and for preventing incorrect zero/allocation interpretation.

Most functions are annotated with coroutine and graph-lock expectations, reflecting QEMU block-layer concurrency requirements.
