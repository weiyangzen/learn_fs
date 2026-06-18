# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_recv.c

This file implements the receive side of ZFS send/receive streams. It validates stream begin records, creates or resumes temporary receive datasets, reads stream records, applies them to the DMU, manages raw/encrypted receive state, finalizes snapshots, and cleans up failed receives.

Core responsibilities:
- Defines receive tunables and tags: `zfs_recv_queue_length`, `dmu_recv_tag`, and temporary clone name `%recv`.
- Validates begin records for existing targets, new targets, clone receives, resumable receives, raw/encrypted streams, feature compatibility, snapshot/filesystem limits, origin GUIDs, and force behavior.
- Creates receive targets in sync context:
  - Existing filesystem receives create a temporary `%recv` clone.
  - New filesystem receives create a new dataset.
  - Raw full receives defer objset physical creation until stream processing can consume raw encryption payload metadata.
  - Resumable receives store resume metadata in dataset ZAP fields.
- Supports resume begin by finding an inconsistent `%recv` or target dataset, validating saved resume fields, toguid/fromguid, ownership, and snapshot state, then re-owning it for receive.
- Reads stream records from a vnode, updates Fletcher checksums, supports byteswapped streams, validates record checksums, and allocates payload buffers or ARC buffers.
- Uses a two-thread pipeline in `dmu_recv_stream()`:
  - Reader thread reads records, validates payload/checksum, issues prefetches, and enqueues records.
  - Writer thread dequeues records and applies DMU changes.
- Applies all replay record types:
  - `DRR_OBJECT`: claim/reclaim dnodes, update bonus data, checksum/compress settings, raw dnode geometry, spill flags, and object-range crypto params.
  - `DRR_FREEOBJECTS`: frees object ranges.
  - `DRR_WRITE`: assigns loaned ARC buffers into object offsets.
  - `DRR_WRITE_BYREF`: handles dedup streams by copying from referenced datasets via GUID map.
  - `DRR_WRITE_EMBEDDED`: writes embedded blocks for non-raw streams.
  - `DRR_SPILL`: writes or ignores spill blocks depending on stream flags.
  - `DRR_FREE`: frees byte ranges.
  - `DRR_OBJECT_RANGE`: captures raw dnode-block crypto params.
  - `DRR_END`: verifies final stream checksum.
- Manages dedup receive GUID maps using AVL trees registered through `zfs_onexit`, with dataset ownership cleanup callbacks.
- Handles raw receive encryption payloads from the `DRR_BEGIN` nvlist through `dsl_crypto_recv_raw()` and delayed key updates for existing datasets.
- Maintains resumable receive progress by saving object, offset, and bytes-read fields during successful write records.
- Finalizes receives in sync context:
  - For existing targets, swaps the `%recv` clone into the origin head, optionally destroys newer snapshots when forced, snapshots the updated head, and destroys the temporary receive dataset.
  - For new targets, snapshots the received dataset and clears inconsistent/resume state.
  - Sets snapshot creation time, GUID, and raw IV set GUID where supplied.
- Cleans failed receives with `dmu_recv_cleanup_ds()`, preserving resumable inconsistent datasets when possible or destroying non-resumable partial receives.

Important control-flow notes:
- `dmu_recv_begin()` must be followed by `dmu_recv_stream()` on success, and `dmu_recv_stream()` must be followed by `dmu_recv_end()` on success.
- Receive datasets are intentionally marked `DS_FLAG_INCONSISTENT` during stream application and cleared only during successful end sync.
- The receive reader keeps an ordered object ignore list to avoid unsafe/useless prefetches when object allocation or blocksize changes.
- Resume correctness depends on ordered write records and validation of begin payload resume object/offset against dataset ZAP state.
- Raw receive path preserves on-disk encrypted bytes, dnode layout, byteorder, salt, IV, MAC, compression type, and maxblkid.

Key dependencies:
- DMU object, dnode, ARC buffer, dbuf, and transaction APIs for replaying stream records.
- DSL dataset/dir/snapshot/clone swap/destroy APIs for receive target lifecycle.
- SPA feature checks for embedded data, LZ4, large blocks, large dnodes, extensible dataset, and encryption.
- ZAP/NVList for resume metadata and raw encryption payloads.
- `zfs_onexit` for dedup stream GUID map lifetime.

Risk-sensitive invariants:
- Stream records must be ordered for resumable receive state.
- Raw receives cannot mix with embedded data and require spill-block stream flags.
- Existing encrypted filesystem replacement is restricted because old and new encryption key state cannot safely coexist during forced full replacement.
- Inconsistent datasets must not be exposed as normal mounted state before `dmu_recv_end_sync()` completes.
