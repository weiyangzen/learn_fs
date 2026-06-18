# Research: sources/object-store/rustfs/crates/ecstore/src/set_disk.rs

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008253`: lines 1-6888, `Docs/researches/chunks/subset-b-008253_research.md`
- `subset-b-008254`: lines 6889-6987, `Docs/researches/chunks/subset-b-008254_research.md`

## Chunk Research

### subset-b-008253: lines 1-6888

# sources/object-store/rustfs/crates/ecstore/src/set_disk.rs lines 1-6888

## Scope And Purpose

This chunk is the primary `SetDisks` implementation for RustFS erasure-coded object storage. It wires a set of `DiskStore` drives, erasure metadata (`FileInfo`/`FileMeta`), namespace locking, bitrot-protected readers/writers, multipart upload state, transition/restore workflows, healing decisions, capacity accounting, and admin storage snapshots into the `StorageAPI` trait family.

The file is not just glue. It implements the object I/O control plane for a single erasure set: reading object metadata under quorum, streaming erasure-decoded object data, writing encoded shards to temporary storage and atomically promoting them, updating metadata and tags, deleting versions and delete markers, completing multipart uploads, sending heal requests, and exposing operational state for management APIs. Helper modules under `set_disk/` provide lower-level read/write/metadata/list/lock/heal/multipart routines; this file composes them into bucket/object/list/multipart/heal trait methods.

The requested range includes the top-level implementation and most of the local unit tests. The final file tail after line 6888 is outside this chunk and is not covered here.

## Important APIs, Types, And Functions

- `SetDisks` is the central type. It stores `locker_owner`, shared `disks`, `set_endpoints`, drive counts, parity defaults, set/pool indexes, `FormatV3`, distributed `LockClient`s, a local lock manager, and a currently mostly-disabled disk health cache.
- `ObjectLockDiagGuard` wraps a `NamespaceLockGuard` and records hold duration metrics/logs when object-lock diagnostics are enabled. `acquire_read_lock_diag()` and `acquire_write_lock_diag()` create these guards and record slow acquisition telemetry.
- Environment-tuned helpers include `get_duplex_buffer_size()`, `get_lock_acquire_timeout()`, `is_object_lock_diag_enabled()`, slow acquire/hold thresholds, `is_lock_optimization_enabled()`, `is_deadlock_detection_enabled()`, and issue-specific diagnostics behind `RUSTFS_ISSUE3031_DIAG_ENABLE`.
- Capacity helpers `capacity_scope_from_disks()` and `record_capacity_scope_if_needed()` convert successful disk sets into `CapacityScope`/`CapacityScopeDisk` records and update global dirty/capacity-scope accounting.
- Metadata helpers in this file include `strip_internal_multipart_metadata()`, `should_persist_encryption_original_size()`, explicit null-version mapping, small-write path classification, tiered decommission quorum construction, delete replication-state helpers, dangling object detection helpers, storage-class classifiers, ETag matching, multipart MD5/checksum helpers, and part-marker pagination.
- `impl ObjectIO for SetDisks` implements `get_object_reader()` and `put_object()`. Reads resolve metadata through `get_object_fileinfo()`, handle delete markers and transitioned objects, create a duplex pipe, and spawn a decode task. Writes choose parity from storage class/defaults, create erasure metadata, encode through bitrot writers, choose inline/single-block/pipeline write paths, rename temp data into place under a write lock, clean temporary data, and return `ObjectInfo`.
- `impl NamespaceLocking` builds either a distributed namespace lock with majority quorum over `self.lockers` when distributed erasure is active, or a local `LocalLock` backed by the global lock manager otherwise.
- `impl ObjectOperations` implements self-copy metadata updates, delete object/version/batch delete, object info, object metadata/tag updates, lifecycle transition to remote tier, restore from tier, and object-integrity verification by streaming to sink.
- `impl MultipartOperations` implements upload creation, part upload, part listing, upload listing, multipart info, abort, and complete. Completion validates ETags, minimum part size, multipart checksum mode, optional full-object checksum, object size metadata, encryption original-size metadata, and then promotes multipart staging data into the live object namespace.
- `impl HealOperations` exposes `heal_object()` in this file and delegates detailed healing helpers to `set_disk/heal.rs`. The local heal utilities include dangling object/dir detection, part verification status aggregation, and `should_heal_object_on_disk()`.
- Admin/storage helpers `storage_info_snapshot()`, `local_storage_info_snapshot()`, `disk_inventory()`, `get_disks_info()`, `build_runtime_snapshot_disk()`, `get_storage_info()`, and `stat_all_dirs()` produce management-facing drive and backend information.
- Several trait methods are intentionally unimplemented in this chunk: bucket operations, list operations, multipart copy, format/bucket heal, pool/set lookup, and abandoned-part checks.

## Control Flow

`get_object_reader()` starts by optionally taking a shared namespace lock. It records deadlock/debug metrics, reads quorum-resolved metadata with `get_object_fileinfo(bucket, object, opts, true)`, converts it to `ObjectInfo`, rejects current delete markers as file-not-found or method-not-allowed, returns an empty cursor for zero-byte objects, and routes transitioned remote objects through lifecycle tier readers. For local objects, it may drop the read lock immediately after metadata resolution when lock optimization is enabled. It then builds a Tokio duplex stream sized by `RUSTFS_DUPLEX_BUFFER_SIZE`, constructs the user-facing `GetObjectReader` with range handling, and spawns `get_object_with_fileinfo()` to erasure-decode the requested range into the duplex writer.

`put_object()` snapshots disks, optionally takes an early write lock for HTTP preconditions, merges user/evaluated metadata, chooses parity from storage class or defaults, creates a fresh `FileInfo` and `data_dir`, shuffles disks and metadata according to erasure distribution, and writes shards into `RUSTFS_META_TMP_BUCKET/<tmp>/part.1`. It creates one bitrot writer per online disk, requires write quorum before encoding, replaces the input stream while erasure encoding runs, and selects an inline, single-block non-inline, or normal pipeline path for small payloads. After verifying the written size, it fills metadata, ETag, actual size, checksum, inline data, object parts, compression size, data-movement state, and versioning flags. A write lock is acquired for commit if it was not already held. `rename_data()` promotes temporary data and metadata into the target bucket/object, `commit_rename_data_dir()` cleans old data dirs when needed, capacity scope is recorded, temporary staging is deleted, and the final `ObjectInfo` is returned.

Batch delete first builds a unique-object batch lock request. In distributed erasure it calls `acquire_dist_delete_object_locks_batch()`, which sends lock batches to every `LockClient`, resolves each object as soon as write quorum succeeds or becomes impossible, rolls back partial locks for failed objects, and asynchronously cleans up late successful locks from slow clients. In local mode it uses `GlobalLockManager::acquire_locks_batch()`. The method builds per-object `FileInfoVersions`, inserts delete markers for versioned/suspended buckets, preserves explicit null-version reporting, writes `delete_versions()` across all disks, reduces errors by write quorum, records capacity scope, and releases distributed locks.

Single-object `delete_object()` takes a write lock unless the request is a broad prefix delete or explicitly `no_lock`. Prefix deletes dispatch to `delete_prefix()`. Normal deletes fetch current object info/quorum, consult replication policy with `check_replicate_delete()`, compute mark-delete/delete-marker semantics via `resolve_delete_version_state()`, builds a version/delete-marker `FileInfo`, calls `delete_object_version()`, records capacity scope, and returns an `ObjectInfo` that reflects the delete result.

Metadata-only copy is restricted to self-copy. If source metadata is not metadata-only and a pre-fetched `PutObjReader` exists, self-copy can write tiered data back locally. Otherwise the metadata path reads all xl metadata, obtains quorum, rejects delete markers, updates metadata/ETag/mod-time/version, and either writes unique file info for version-only copy or calls `update_object_meta_with_opts()` for normal metadata replacement.

Multipart flow starts with `new_multipart_upload()`, which creates erasure metadata under `RUSTFS_META_MULTIPART_BUCKET`, includes internal bucket/object metadata keys, stores requested multipart checksum type, and returns a base64 deployment-prefixed upload id. `put_object_part()` validates the upload id and checksum mode, writes a part into a temp path with erasure/bitrot encoding, records per-part metadata beside the part, and atomically renames it into the multipart upload directory. `list_object_parts()` lists part numbers that appear on read quorum of disks, applies part-number marker pagination, reads part metadata, and strips internal multipart metadata from the response. `complete_multipart_upload()` reads requested part metadata, validates part ids and normalized ETags, enforces the 5 MiB minimum on all but the final part, validates or combines checksums, removes multipart-only metadata, computes object ETag and size fields, persists encryption original size when SSE metadata is present, cleans unused part metadata, takes the commit write lock, promotes the multipart directory into the live object namespace, schedules healing if versions were observed, asynchronously deletes the multipart staging path, and returns the completed `ObjectInfo`.

Lifecycle transition streams the local object through `get_object_with_fileinfo()` into a remote tier client, preserves selected user/system/object-lock metadata, then marks the local `FileInfo` as transitioned and calls `delete_object_version()` to remove local data. Restore performs the reverse: single-part restores use `put_object()`, multi-part restores create a new multipart upload, fetch each remote part range, upload each part locally, then complete the multipart upload.

Healing-facing control flow collects xl metadata and part status across disks. `is_object_dangling()` compares metadata not-found/corrupt counts and part missing/corrupt counts against data/parity thresholds. `disks_with_all_parts()` rejects outdated metadata, validates erasure distribution, marks inline shards as present from metadata, and runs either `verify_file()` for deep scans or `check_parts()` for normal scans. `should_heal_object_on_disk()` decides whether to rewrite metadata, data, or neither based on metadata errors, metadata equality, and per-part error codes.

## State And Persistence Behavior

Live object state is persisted as xl metadata and erasure shards across the configured drives. Object writes stage data in `RUSTFS_META_TMP_BUCKET` and only become visible after `rename_data()` writes per-disk metadata into the target bucket/object path. Multipart state is persisted under `RUSTFS_META_MULTIPART_BUCKET` using hashed upload directories, with upload metadata at the root and part data/part metadata under the upload `data_dir`. Abort and post-complete cleanup delete these multipart paths.

`FileInfo` is the durable object/version record. This file mutates fields for erasure layout, `data_dir`, `version_id`, `versioned`, `deleted`, `mark_deleted`, `mod_time`, `metadata`, `parts`, `checksum`, transition state, replication state, inline-data flags, and data-movement flags. Inline small objects store shard bytes in metadata instead of separate part files; the heal scan treats such shards as present once metadata reads successfully.

Versioning behavior is encoded into delete and write metadata. Versioned puts create a new UUID when the caller does not supply one. Suspended/null-version deletes map the explicit nil UUID to stored `None` through `delete_file_info_version_id()` while preserving nil UUIDs in delete responses. `resolve_delete_version_state()` handles source delete-marker purges, replica delete-marker updates, data movement of missing markers, and completed purge status so deletes do not accidentally recreate markers.

Replication and lifecycle state is persisted inside `FileInfo` metadata/state fields. Delete replication decisions are attached to `ObjectOptions` and copied into delete `FileInfo`s. Transition completion stores remote object name, tier, remote version id, and transition status before local cleanup. Restore updates metadata and sends restore-completed events after local reconstruction.

Object-lock and precondition state are not persisted here, but metadata updates enforce retention semantics with `check_object_lock_retention_update()`, and writes/deletes/copies use namespace locks to serialize object mutations. Diagnostics persist only through metrics/logs, not object metadata.

Capacity state is reported to `rustfs_object_capacity` after successful write/delete/promote operations. Admin disk capacity state is partly live-probed and partly cached as each `DiskStore`'s last capacity snapshot, allowing offline/suspect drive reporting without forcing every admin request to hit the filesystem.

## Dependencies And Integration Points

This file depends on RustFS disk APIs for all persistence primitives: `DiskStore`, `DiskAPI`, `write_metadata`, `delete_version`, `delete_versions`, `list_dir`, `check_parts`, `verify_file`, `disk_info`, temp/meta buckets, `DeleteOptions`, `ReadOptions`, and format loading. The lower-level helpers are split into sibling modules: `set_disk/read.rs`, `write.rs`, `metadata.rs`, `multipart.rs`, `heal.rs`, `list.rs`, `lock.rs`, and `replication.rs`.

Erasure and bitrot integration is central. `erasure_coding::Erasure` performs encode/decode and shard-size calculations, while `create_bitrot_writer()` and `create_bitrot_reader()` protect shard writes and reads using `HashAlgorithm::HighwayHash256S` or per-file checksum information. `PutObjReader`, `HashReader`, ETag resolution, compression index extraction, and checksum APIs come from the store/rio layers.

Locking integrates with `rustfs_lock` through local and distributed namespace locks. Distributed erasure uses the configured locker clients and majority quorum; non-distributed erasure uses the process-global local lock manager. Batch delete has custom quorum/cleanup logic on top of `LockClient::acquire_locks_batch()` and `release_locks_batch()`.

Bucket configuration systems influence behavior: `BucketVersioningSys` drives delete-marker/version decisions, global storage-class config chooses parity and inline thresholds, lifecycle operations provide transition object naming/readers and restore options, object-lock code checks retention mutations, and replication helpers decide delete replication state.

External integrations include lifecycle tier drivers through `GLOBAL_TierConfigMgr`, event notification through `send_event()` for transition and restore, heal-channel requests through `rustfs_common::heal_channel`, admin structs in `rustfs_madmin`, capacity accounting in `rustfs_object_capacity`, and metrics/tracing for locks, writes, multipart, and heal diagnostics.

## Risks And Edge Cases

- `HealOperations::heal_object()` in this file calls `self.heal_object()` again after setting `inner_opts.no_lock = true`. Because there is also an inherent helper of the same name in `set_disk/heal.rs`, this should be checked carefully for method-resolution intent; as written in the trait impl it risks recursive dispatch rather than delegation if Rust resolves to the trait method.
- `stat_all_dirs()` only pushes results for flattened present disks, so its returned error vector can be shorter than the input disk vector and lose positional correspondence for `None` disks.
- Several operations call `disk.is_online().await` inside loops after already selecting disks. Runtime state can change between writer creation, encode, rename, and final metadata selection, so quorum reduction must remain the source of truth.
- `put_object()` and `put_object_part()` return early on encode/write failures before some temp cleanup paths. `put_object()` has outer temp cleanup, but `put_object_part()` has a TODO noting temporary directory cleanup on error.
- Lock optimization in `get_object_reader()` intentionally releases the read lock after metadata resolution. This reduces contention but allows object mutation while the spawned read task is still streaming from the resolved data directory; correctness relies on immutable data dirs and rename/delete semantics.
- `complete_multipart_upload()` cleans multipart part metadata before promotion and spawns asynchronous cleanup after success. Failures around promotion or cleanup can leave staging artifacts, and healing is only scheduled when `rename_data()` returns version information.
- Multipart upload ids are deployment-prefixed and base64 encoded, while filesystem paths use decoded/upload UUID material. Callers and tests need to preserve this distinction.
- `list_multipart_uploads()` breaks after the first disk that lists upload ids. This is fast but can miss uploads present only on other quorum disks if the first successful disk is stale.
- Transition has a remote-first commit pattern: remote tier `put_with_meta()` can succeed and local `delete_object_version()` can fail. The code suppresses external lifecycle notification in that case and records partial healing if any disk is missing, but remote/local divergence remains possible.
- Restore multipart path validates `part_info.actual_size > 0`; zero-sized multipart parts or bad actual-size metadata become restore-header error updates.
- `should_prevent_write()` blocks conditional writes if the existing object ETag cannot be obtained and any condition is present. This is conservative but may reject writes that a caller expects to be evaluated by another metadata source.
- Bucket and list trait methods are unimplemented here. Any code path using `SetDisks` directly for bucket creation/listing or object listing must route elsewhere or will panic.
- Several environment switches materially change behavior (`RUSTFS_OBJECT_LOCK_OPTIMIZATION_ENABLE`, lock acquisition timeout, diagnostics, duplex buffer size). Tests and production debugging need to capture these settings.

## Test Signals

The in-file tests cover small but important behavior:

- Disk health cache expiry, part status constants, multipart minimum part size, multipart MD5 and checksum helper behavior, upload-id and multipart hash path generation.
- Distributed namespace locks with mixed healthy/offline lockers, including read quorum success and write quorum failure.
- `no_lock` behavior for copy, delete, and exact prefix delete when an outer write lock is already held; broad prefix delete deliberately avoids locking the literal prefix key.
- Batch distributed delete locks: success with two healthy lockers, rollback when quorum is not reached, early return once quorum is satisfied without waiting for slow lockers, and cleanup of late successes after early failure.
- Metadata quorum helpers: common parity/time/ETag, object modtime/etag/parity extraction, all-not-found vs mixed metadata quorum errors, common data-dir reduction, disk/metadata shuffling, part-error conversion, and data-error matrix population.
- Dangling object helpers: metadata/part not-found counters, object-dir dangling detection, joined error rendering, and `should_heal_object_on_disk()` decisions.
- Admin storage info behavior for online, suspect, and offline runtime drive states, including capacity snapshot fallback.
- List-path recovery after prior walk timeouts for normal buckets and system prefixes, ensuring timeout does not permanently mark disks offline.
- Object-lock retention updates: compliance shortening is blocked while governance shortening with bypass remains allowed.
- Encryption original-size persistence triggers only for SSE-related metadata.
- ETag condition handling through `e_tag_matches()` and `should_prevent_write()`.
- Storage-class validation recognizes the supported S3/RustFS classes and rejects invalid/lowercase strings.
- Range reads with non-zero offsets use the correct shard span length and reproduce the requested payload slice.
- `parts_after_marker()` returns the slice after the marker and returns `None` for missing markers.
- Explicit null-version deletes map nil UUID to stored null version ids.
- Put-object fast path selection uses inline only for inline single-block payloads, uses single-block non-inline for non-inline single-block payloads, and rejects zero, negative, or multi-block payloads.

Broader verification should include integration tests for full put/get/delete/multipart/transition/restore flows across multiple disks with injected disk failures, bitrot corruption, stale xl metadata, distributed lock failures, remote tier failures, and versioned bucket replication scenarios. The local tests are useful regression signals for helper semantics, but most correctness depends on quorum behavior across real `DiskStore` implementations and the helper modules called from this file.

### subset-b-008254: lines 6889-6987

# sources/object-store/rustfs/crates/ecstore/src/set_disk.rs lines 6889-6987

## Scope And Purpose

This chunk is the tail of the `set_disk.rs` unit-test module. It does not add production runtime behavior directly; instead, it pins down three narrow but important contracts in the erasure set implementation:

- small object and multipart part write-path classification for non-inline, single-block payloads;
- S3-compatible storage-class categorization helpers for cold and infrequent-access classes;
- a regression path for same-bucket/same-key copy of a transitioned, tiered object where `ObjectInfo.metadata_only` is false.

The surrounding production code is in the same file. `classify_small_write_path` and its helpers are used by both `put_object` and `copy_object_part` encoding paths. `is_cold_storage_class` and `is_infrequent_access_class` are exported predicates used to distinguish lifecycle/tiering classes. `SetDisks::copy_object` is the lower erasure-set implementation used by higher-level store and set routing code for self-copy metadata updates, version-only copies, and tiered-object de-tiering.

## Important APIs, Types, And Functions

`should_use_single_block_non_inline_fast_path(is_inline_buffer, object_size, block_size)` returns true only when the input is not inline-buffered and `object_size` is positive and no larger than the erasure block size. The test in this chunk asserts the exact boundary behavior: sizes equal to and below the block size are fast-path candidates, one byte above the block size is not, and zero is not.

`SmallWritePath` is the internal classifier result with `Inline`, `SingleBlockNonInline`, and `Pipeline` variants. `classify_small_write_path` prefers the inline fast path when `is_inline_buffer` is true and the object fits a single block, otherwise uses `SingleBlockNonInline` for non-inline single-block data, and falls back to `Pipeline`.

`is_cold_storage_class(storage_class)` recognizes `DEEP_ARCHIVE`, `GLACIER`, and `GLACIER_IR`. The test also asserts that standard, reduced redundancy, standard infrequent access, and express one-zone classes are not cold classes.

`is_infrequent_access_class(storage_class)` recognizes `ONEZONE_IA`, `STANDARD_IA`, and `INTELLIGENT_TIERING`. The test asserts that standard, reduced redundancy, deep archive, and express one-zone are not infrequent-access classes.

`SetDisks::copy_object` is the lower-level copy entry point under test for the tiered self-copy regression. Relevant inputs are `src_bucket`, `src_object`, `dst_bucket`, `dst_object`, mutable `ObjectInfo`, source options, and destination options. The chunk constructs `ObjectInfo { metadata_only: false, transitioned_object.tier: "NEXTCLOUD", .. }` and calls `copy_object` with identical source and destination keys and `dst_opts.no_lock = true`.

The test uses `SetupTypeGuard::switch_to(SetupType::Erasure)`, `make_test_set_disks`, `LocalClient`, and `GlobalLockManager` to build a minimal erasure-set test environment while avoiding nested lock waits through `no_lock`.

## Control Flow

The small-write test exercises a pure decision path. The helper first rejects inline buffers for the non-inline fast path, then delegates size validation to `object_fits_single_block`, which rejects zero, negative, and `usize` conversion overflow cases and accepts `1..=block_size`. The classifier uses that result to select `SmallWritePath::SingleBlockNonInline` for multipart and non-inline small object writes.

In production, `put_object` calls `classify_small_write_path(is_inline_buffer, data.size(), fi.erasure.block_size)` before choosing among `encode_inline_small`, `encode_single_block_non_inline`, and the normal streaming `encode` pipeline. `copy_object_part` calls the same classifier with `is_inline_buffer = false`; only `SingleBlockNonInline` receives the special single-block encoding path, while `Inline` and `Pipeline` both use normal streaming encode for multipart data.

The storage-class tests are direct predicate checks. They serve as a concise executable mapping from the constants in `config::storageclass` to the semantic categories used by lifecycle/tiering code.

The tiered self-copy regression follows `SetDisks::copy_object`'s initial guard. If `metadata_only` is false, cross-key copies are still rejected with `StorageError::NotImplemented`, but same-key copies are allowed to continue. If `src_info.put_object_reader` is present, the method de-tiers by calling `put_object` for the destination. If no reader is present, same-key copy falls through to the metadata path so callers receive a normal disk, missing-file, or quorum error instead of an early `NotImplemented`.

After the initial same-key check, `copy_object` optionally acquires a write lock unless `dst_opts.no_lock` is true, checks HTTP write preconditions, reads all xl/file metadata from disks, computes read/write quorum, picks a valid `FileInfo`, rejects delete markers, updates metadata, version ID, versioning flags, mod time, and etag, and persists either with `write_unique_file_info` for version-only copies or `update_object_meta_with_opts` for normal metadata replacement.

## State And Persistence Behavior

The small-write and storage-class tests are pure and have no persistent state. Their importance is indirect: changing these helpers changes which erasure encoder path writes object shards and part shards. A misclassification can alter inline data placement, bitrot writer usage, memory behavior, or quorum write behavior.

The tiered self-copy test builds in-memory/minimal local lock state and does not create object shard data. Its expected outcome deliberately allows success or any ordinary storage error except `StorageError::NotImplemented`. That makes the test a guard for routing and validation behavior, not a full persistence test for de-tiering bytes.

The production `copy_object` path is stateful. It reads existing object metadata from the erasure disks, derives quorum from available metadata, mutates `FileInfo` metadata and version fields, and writes metadata back to online disks. For version-only copy it preserves inline-data flags carefully across valid metadata entries before calling `write_unique_file_info`; for ordinary metadata updates it calls `update_object_meta_with_opts` with `replace_user_metadata = true`.

For tiered objects with an available `put_object_reader`, same-key `metadata_only = false` can write remote tier data back to local erasure storage through `put_object`. For tiered objects without a reader, the current lower-level behavior is intentionally to fall through and surface a disk/quorum style error rather than a feature-not-implemented error.

## Dependencies And Integration Points

The small-write path integrates with the erasure coding module and bitrot writer setup in `put_object` and `copy_object_part`. It depends on `HashReader`, erasure block sizing from `FileInfo.erasure.block_size`, write quorum checks, and writer construction for each target disk.

The storage-class predicates depend on `crate::config::storageclass` constants. They are likely consumed by lifecycle, restore, transition, and object classification paths that need different behavior for archive-like classes versus infrequent-access classes.

The tiered copy regression sits at the boundary between higher-level object copy routing and lower-level set operations. `store/object.rs` decides when a self-copy should be metadata-only, version-only, or restored from a tier through `put_object_reader`; `sets.rs` routes between source and destination sets; `SetDisks::copy_object` enforces the final same-key-only lower-copy contract. The test imports `TransitionedObject` from lifecycle operations because tier metadata is represented on `ObjectInfo.transitioned_object`.

Locking is also an integration point. Earlier nearby tests assert `copy_object` honors `dst_opts.no_lock` when an outer write lock is already held and rejects metadata-only cross-key lower copies. This chunk's regression uses the same `no_lock` option to focus on the NotImplemented guard rather than lock acquisition.

## Risks And Edge Cases

The single-block fast path is boundary-sensitive. Treating zero-length payloads as single-block writes, accepting payloads larger than the block size, or failing to distinguish inline from non-inline buffers would send data through the wrong encoder and could affect shard layout or read compatibility.

Storage-class classification can drift as new classes are added. The predicates are explicit allowlists, so adding a new archive or infrequent-access class elsewhere without updating these helpers would silently route that class as a normal/frequent class.

The tiered self-copy test documents a historical regression, but the embedded comment is stale relative to the current implementation: it says the test currently fails because an old guard unconditionally rejected `!metadata_only`, while the current `copy_object` implementation already allows same-key `metadata_only = false` and only rejects cross-key copies. Keeping that comment stale could confuse future debugging even though the test assertion remains useful.

The regression test is intentionally weak on persistence. It only rejects `StorageError::NotImplemented`; it does not verify that tier data is fetched, written locally, metadata transitions are cleared or preserved correctly, or storage-class headers are applied. Those behaviors need broader integration tests with a real `put_object_reader` and readable object metadata.

Because same-key path checks use `path_join_buf(&[bucket, object])`, correctness depends on consistent path normalization. Any change in bucket/object path joining semantics could alter whether a copy is considered self-copy or cross-key.

## Test Signals

The chunk provides direct unit-test signals:

- `put_object_part_fast_path_selection_matches_single_block_non_inline_rules` guards exact size and inline-buffer boundaries for multipart part fast-path selection.
- `test_is_cold_storage_class` guards the cold-storage allowlist and several explicit non-cold classes.
- `test_is_infrequent_access_class` guards the infrequent-access allowlist and several explicit frequent or archive classes.
- `copy_object_tiered_self_copy_does_not_return_not_implemented` guards same-key tiered self-copy routing by failing only if `copy_object` returns `StorageError::NotImplemented`.

Useful follow-up test coverage would include an end-to-end tiered self-copy with `put_object_reader = Some(...)` that verifies bytes and metadata after `put_object`, plus storage-class predicate tests updated whenever new S3-compatible storage-class constants are introduced.
