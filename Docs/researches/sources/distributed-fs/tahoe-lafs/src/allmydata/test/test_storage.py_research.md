# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage.py

## Purpose
This file is the broad unit and integration-style test surface for Tahoe-LAFS local storage primitives. It covers storage-index encoding, immutable share containers, mutable share containers, bucket writers/readers, Foolscap-facing bucket wrappers, storage-server allocation and lease semantics, corruption advisory persistence, MDMF/SDMF mutable layout proxies, latency statistics, schema compatibility, `LeaseInfo`, and `_WriteBuffer` batching. It is intentionally low-level: most tests instantiate `StorageServer`, `BucketWriter`, `BucketReader`, `ShareFile`, `MutableShareFile`, and layout proxies directly instead of going through a full node.

## Important APIs, Types, And Helpers
The main test classes are `UtilTests`, `Bucket`, `BucketProxy`, `Server`, `MutableServer`, `MDMFProxies`, `Stats`, `ShareFileTests`, `MutableShareFileTests`, `LeaseInfoTests`, and `WriteBufferTests`. Local helpers include `bchr`, `FakeStatsProvider`, `RemoteBucket`, `make_lease`, `Server.allocate`, `MutableServer.allocate`, MDMF/SDMF share builders, and `compare_leases_without_timestamps`.

The production APIs under test are `storage_index_to_dir`, `si_b2a`, `si_a2b`, `get_share_file`, `BucketWriter`, `BucketReader`, `FoolscapBucketWriter`, `FoolscapBucketReader`, `WriteBucketProxy`, `WriteBucketProxy_v2`, `ReadBucketProxy`, `StorageServer`, `FoolscapStorageServer`, `MutableShareFile`, `ShareFile`, `LeaseInfo`, `MDMFSlotWriteProxy`, `MDMFSlotReadProxy`, `SDMFSlotWriteProxy`, and `_WriteBuffer`. The file also validates protocol constants such as `MDMFHEADER`, `MDMFOFFSETS`, `MDMFSIGNABLEHEADER`, `SIGNED_PREFIX`, field sizes for private keys/signatures/verification keys/share hash chains, and schema collections `ALL_IMMUTABLE_SCHEMAS` and `ALL_MUTABLE_SCHEMAS`.

## Control Flow
The immutable bucket tests build incoming and final filesystem paths, write byte ranges through `BucketWriter`, close or abort writers, then read finalized data through `BucketReader`. Several tests use Hypothesis to explore overlapping writes, conflicting writes, required-range tracking, read truncation at the end of share data, and `_WriteBuffer` coalescing.

The storage-server tests create a `StorageServer` attached to a `LoggingServiceParent`, allocate immutable buckets, write or abort writers, and inspect the resulting bucket readers, available-space accounting, leases, readonly/discard behavior, sparse-file behavior, and advisory files. Foolscap tests wrap the local server with `FoolscapStorageServer` or the writer/reader wrappers and use `RemoteBucket.callRemote` to simulate remote method dispatch while counting mutable read/write RPCs.

The mutable-server tests drive `slot_testv_and_readv_and_writev` and `slot_readv` directly. They create mutable shares, exercise test/write/read vector semantics, verify operators, ensure reads happen before writes in combined operations, validate write-enabler failures, confirm zero-fill behavior when writes extend past EOF, test truncation and deletion via `new_length=0`, and check lease renewal/addition behavior across share growth.

The MDMF/SDMF proxy tests hand-construct binary shares. `build_test_mdmf_share` writes the checkstring, encoding parameters, offset table, encrypted private key, share hash chain, signature, verification key, share data, and block hashes. `build_test_sdmf_share` constructs legacy SDMF layout. Tests then publish through `MDMFSlotWriteProxy` or `SDMFSlotWriteProxy`, read through `MDMFSlotReadProxy`, and assert ordering, offset, checkstring, prefetch, tail-segment, empty-file, and legacy compatibility behavior.

## State And Persistence Behavior
The tests persist share state under relative `storage/...` work directories, mirroring Tahoe-LAFS storage layout with `shares`, prefix directories, storage-index directories, incoming temporary share paths, finalized share files, and `corruption-advisories`. Immutable uploads create incoming writers that become readable only after close; abort and disconnect paths must remove provisional allocation and temporary files. Mutable writes alter share files in place and can delete a share and its storage-index directory when truncated to zero.

Lease state is stored inside immutable and mutable share containers. Tests distinguish renewing an existing lease from adding a new one, validate lease serialization lengths, verify renew/cancel secret matching, ensure overflow attempts leave share file bytes unchanged, and assert optional `renew_leases=False` paths leave grant timestamps or lease lists untouched. Clock-controlled tests assert expiration times use `DEFAULT_RENEWAL_TIME`.

Disk-space behavior is stateful. `FakeDisk` patches `fileutil.get_disk_stats` to force `NoSpace` for additional immutable/mutable leases and corruption reports. Reserved-space tests count provisional allocations while writers are open, then real allocation overhead after close. Sparse-file tests are skipped on platforms where they are too expensive.

## Dependencies And Integration Points
The file depends on Twisted Trial, Deferreds, `Clock`, Hypothesis, `testtools.matchers`, and Tahoe test utilities (`LoggingServiceParent`, `FakeDisk`, `FakeCanary`, `upload_immutable`, `upload_mutable`). It integrates with local storage modules (`server`, `immutable`, `mutable`, schemas, lease/common/share helpers), immutable layout proxies, mutable layout proxies, Foolscap wrappers, and the storage-client `_StorageServer` adapter used by mutable layout proxies.

Important integration points are the Foolscap method names (`slot_readv`, `writev` variants), `StorageServer.get_version` capability flags (`prevents-read-past-end-of-share-data`, `maximum-immutable-share-size`, `maximum-mutable-share-size`, `available-space`, `fills-holes-with-zero-bytes`), and on-disk compatibility with older immutable and SDMF formats.

## Risks And Edge Cases
High-risk areas covered include overlapping immutable writes, write conflicts, read-past-share-data leakage, stale incoming writers, disconnect cleanup, reserved-space accounting, corruption advisory persistence under low disk, bad container magic/version handling, mutable conditional writes, zero-fill after truncation, deletion of final mutable shares, lease-table relocation when containers grow, lease-count overflow, and MDMF layout ordering. MDMF-specific risks include invalid salt/root hash/block sizes, too many blocks, publishing with stale checkstrings, uncoordinated writes, prefetch cache correctness, and SDMF fallback.

Some risks remain implicit: many tests depend on relative `storage/...` paths and cleanup behavior in test infrastructure; large-share behavior is skipped on common platforms or low-disk environments; several MDMF tests use simplified keys/hash bytes rather than cryptographic end-to-end verification; and error-message assertions can be brittle when migration diagnostics change.

## Test Signals
Passing this file signals that core local storage semantics are stable across immutable, mutable, Foolscap-wrapper, and layout-proxy layers. It also signals compatibility across mutable and immutable schema variants because Hypothesis samples all schema collections. The tests are a strong regression net for storage persistence, lease accounting, allocation cleanup, protocol layout, and storage capability advertisement.
