# File Research: sources/virtualization/spdk/lib/blob/blobstore.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9615, source bytes 262078, report `Docs/researches/chunks/chunk_sources_virtualization_spdk_lib_blob_blobstore_c_1_1_9615_123117d3cfe4_research.md`
- chunk 2: lines 9616-10533, source bytes 25219, report `Docs/researches/chunks/chunk_sources_virtualization_spdk_lib_blob_blobstore_c_2_9616_10533_f8d9c18fc284_research.md`

## Chunk Research

### Chunk 1: lines 1-9615

# Chunk Research: sources/virtualization/spdk/lib/blob/blobstore.c lines 1-9615

## Scope

This chunk covers the first 9,615 lines of SPDK's `lib/blob/blobstore.c` in subset A (`sources/virtualization/spdk`). It contains most of the blobstore core: option initialization, blob allocation/free, metadata parse/serialize/load/persist, blobstore init/load/dump/unload/destroy, public blob create/open/close/delete/resize/I/O APIs, snapshot/clone/inflate/parent-changing flows, shallow copy, cluster allocation/free coordination, iteration, and the start of xattr accessors.

Report written to `Docs/researches/chunks/chunk_sources_virtualization_spdk_lib_blob_blobstore_c_1_1_9615_123117d3cfe4_research.md`.

## Major APIs And Entry Points

- Blobstore lifecycle: `spdk_bs_init()`, `spdk_bs_load()`, `spdk_bs_dump()`, `spdk_bs_unload()`, `spdk_bs_destroy()`
- Blob lifecycle: `spdk_bs_create_blob[_ext]()`, `spdk_bs_open_blob[_ext]()`, `spdk_blob_close()`, `spdk_blob_sync_md()`, `spdk_blob_resize()`, `spdk_bs_delete_blob()`
- I/O: `spdk_blob_io_read/write/unmap/write_zeroes()`, `spdk_blob_io_readv/writev[_ext]()`
- Snapshot/clone/parent: `spdk_bs_create_snapshot()`, `spdk_bs_create_clone()`, `spdk_bs_inflate_blob()`, `spdk_bs_blob_decouple_parent()`, `spdk_bs_blob_shallow_copy()`, `spdk_bs_blob_set_parent()`, `spdk_bs_blob_set_external_parent()`
- Iteration/xattrs: `spdk_bs_iter_first()`, `spdk_bs_iter_next()`, `spdk_blob_set_xattr()`, `spdk_blob_remove_xattr()`, and `spdk_blob_get_xattr_value()` starts at the chunk tail.

## Core Findings

The chunk’s central invariant is that metadata operations run on `bs->md_thread`, enforced by `blob_verify_md_op()`. Allocation state is protected by `bs->used_lock`, with separate maps for metadata pages, blob ids, open blob ids, and data clusters. Blob metadata has `active` and `clean` copies so in-flight persists can complete without losing newer dirty changes.

Metadata persistence is crash-aware: mark super dirty, write new non-root pages, write root page last, then zero old pages and clear/release truncated clusters and extent pages. Loading validates CRCs and descriptors, then either uses persisted masks or replays metadata pages for recovery when the store is dirty/old/forced.

The data path maps allocated I/O to the primary device and unallocated thin ranges to a backing device. Writes to unallocated thin clusters allocate/copy-on-write a cluster, optionally copying from a snapshot/external backing device, then update metadata on the md thread. Cross-cluster requests are split.

Snapshot, clone, delete, inflate, and parent-change operations are high-risk state machines. They freeze I/O, use internal xattrs for recovery markers, temporarily override `md_ro`, update parent/backing devices, and rely on cleanup callbacks to restore locks and flags.

## Cross-Chunk References

This chunk declares and calls external snapshot helpers whose definitions are outside the range: `blob_esnap_channel_compare()`, `blob_esnap_destroy_bs_dev_channels()`, `blob_esnap_destroy_bs_channel()`, and `blob_set_back_bs_dev_frozen()`. The remaining xattr/status/query APIs continue after line 9615.

### Chunk 2: lines 9616-10533

# Chunk Research: sources/virtualization/spdk/lib/blob/blobstore.c lines 9616-10533

## Scope

This report covers only `sources/virtualization/spdk/lib/blob/blobstore.c` lines 9616-10533 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify helper definitions, callback contexts, and earlier load/esnap setup paths referenced by this chunk. This is the final chunk of the file; it closes public blob property helpers, implements blobstore growth paths, manages external-snapshot backing-device channels, exposes esnap accessors, and registers logging/tracing.

## APIs And Entry Points

- `spdk_blob_get_xattr_value()` returns a public xattr value pointer and length after `blob_verify_md_op()` validates metadata-thread context.
- `spdk_blob_get_xattr_names()`, `spdk_xattr_names_get_count()`, `spdk_xattr_names_get_name()`, and `spdk_xattr_names_free()` expose a transient array of public xattr name pointers.
- `spdk_bs_get_bstype()` and `spdk_bs_set_bstype()` get/set the blobstore type field by value.
- `spdk_blob_is_read_only()`, `spdk_blob_is_snapshot()`, `spdk_blob_is_clone()`, `spdk_blob_is_thin_provisioned()`, and `spdk_blob_is_esnap_clone()` expose blob state predicates.
- `spdk_blob_get_parent_snapshot()` and `spdk_blob_get_clones()` query the in-memory snapshot/clone lists.
- `spdk_bs_grow()` loads a blobstore on a resized device and grows on-disk metadata during load.
- `spdk_bs_grow_live()` grows an already-loaded blobstore on its metadata thread.
- Esnap APIs: `spdk_blob_get_esnap_id()`, `spdk_blob_set_esnap_bs_dev()`, `spdk_blob_get_esnap_bs_dev()`, and `spdk_blob_is_degraded()`.
- Internal esnap channel helpers include `blob_esnap_get_io_channel()`, `blob_esnap_destroy_bs_dev_channels()`, `blob_esnap_destroy_one_channel()`, and `blob_esnap_destroy_bs_channel()`.
- The file ends with `SPDK_LOG_REGISTER_COMPONENT(blob)`, `SPDK_LOG_REGISTER_COMPONENT(blob_esnap)`, and `SPDK_TRACE_REGISTER_FN(blob_trace, "blob", TRACE_GROUP_BLOB)`.

## Control Flow

Xattr name enumeration is two-pass: count `TAILQ` entries, allocate one `struct spdk_xattr_names` plus pointer slots, then store borrowed `xattr->name` pointers. The public wrapper only enumerates user-visible xattrs, not internal xattrs.

Blob snapshot/clone queries are list based. `spdk_blob_is_snapshot()` checks `bs->snapshots`; `spdk_blob_is_clone()` treats a non-invalid, non-external parent id as a clone and asserts thin provisioning. `spdk_blob_get_clones()` uses the usual SPDK sizing pattern: return `-ENOMEM` with required count when the caller buffer is missing or too small.

`spdk_bs_grow()` validates the device/options, allocates load state, reads and validates the super block, then optionally grows the on-disk used-cluster mask and super block before resuming normal load. Growth is refused for unclean blobstores.

`spdk_bs_grow_live()` runs on `bs->md_thread`, reads the super block, rejects shrink/no-space cases, writes an updated dirty super block, then swaps in a larger `used_clusters` bit pool under `bs->used_lock`. It intentionally leaves the blobstore unclean until a later clean unload writes the rest of used metadata.

Esnap channel lookup is lazy per blobstore channel. `blob_esnap_get_io_channel()` checks an RB tree by blob id, creates a backing-device channel on miss, inserts it, and returns it. Teardown either removes channels for one blob across all blobstore channels, optionally aborting queued I/O, or removes all esnap channels when a blobstore channel is destroyed.

`spdk_blob_set_esnap_bs_dev()` delegates to earlier freeze/hotplug machinery: freeze blob I/O, destroy cached esnap channels, optionally update parent references, release the old backing device, install the new `back_bs_dev`, unfreeze, and complete.

## State, Dependencies, Risks

The xattr names object owns only the pointer array; name strings are still owned by the blob xattr list. Growth mutates super-block fields and runtime accounting including `size`, `used_cluster_mask_len`, `total_clusters`, `total_data_clusters`, `num_free_clusters`, `used_clusters`, `open_blobids`, `super_blob`, and `bstype`.

This chunk depends on SPDK `TAILQ`/`RB` containers, bit arrays/pools, metadata sequences, DMA allocation, thread affinity, IO channel iteration, blobstore LBA conversion helpers, `struct spdk_bs_dev` callbacks, and earlier helpers such as `blob_verify_md_op()`, `blob_is_esnap_clone()`, `bs_alloc()`, `bs_super_validate()`, `bs_write_super()`, `bs_load_read_used_pages()`, and `blob_set_back_bs_dev()`.

Key risks: borrowed xattr-name lifetime, grow requiring clean metadata, metadata reserved-space limits for the expanded used-cluster mask, live-grow crash consistency after only the super block is written, per-thread serialization assumptions in the esnap RB tree, and queued I/O aborts during esnap backing-device replacement.

## Cross-Chunk References

- Previous chunk defines xattr set/remove/get helpers and continues into `spdk_blob_get_xattr_value()` at line 9616.
- Earlier initialization defines `blob_esnap_channel`, RB tree generation, `blob_is_esnap_clone()`, metadata-thread verification, snapshot lookup, backing-device reference release, and `set_bs_dev_ctx`.
- Earlier load/recovery code owns `spdk_bs_load_ctx`, `bs_load_read_used_pages()`, and `bs_load_complete()`, which `spdk_bs_grow()` resumes after optional growth.
- Earlier snapshot and parent-setting paths populate `bs->snapshots`, clone lists, `parent_id`, esnap xattrs, and `back_bs_dev`.
- There is no next chunk; the file ends at line 10533 with logging and trace registration.
