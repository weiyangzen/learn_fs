# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_upload.py

## Purpose
This module is the main test surface for immutable upload behavior in Tahoe-LAFS. It verifies uploadable wrappers, literal-vs-CHK upload selection, storage-index derivation, server selection, share placement, servers-of-happiness semantics, failure diagnostics, bucket abort cleanup, and encryption streaming. It combines small fake remote-storage objects with full no-network grids to cover both algorithm-level and integration-level behavior.

## Important APIs, Types, And Functions
`Uploadable` tests `upload.FileHandle`, `upload.FileName`, and `upload.Data` size/read/close behavior. `FakeStorageServer`, `FakeBucketWriter`, and `FakeClient` emulate Foolscap remote storage, bucket writers, version announcements, allocation failures, full servers, small maximum share sizes, timeouts, and storage broker registration. `GiganticUploadable` simulates boundary sizes without actually reading enormous files. `upload_data`, `upload_filename`, and `upload_filehandle` are convenience wrappers around `Uploader.upload`.

The principal test classes are `GoodServer`, `ServerErrors`, `FullServer`, `ServerSelection`, `StorageIndex`, `FileHandleTests`, `EncodingParameters`, and `EncryptAnUploadableTests`. The local `combinations` and `is_happy_enough` helpers provide a brute-force happiness oracle used to validate share distribution. `EncodingParameters` also provides grid helpers such as `find_all_shares`, `_setup_and_upload`, `_add_server_with_share`, `_copy_share_to_server`, and `_do_upload_with_broken_servers`.

## Control Flow
The early tests drive `Uploader.upload` against `FakeClient`: small zero/short uploads should produce `LiteralFileURI`, larger uploads should produce `CHKFileURI`, and huge uploadables should fail before consuming data. Server selection tests vary `k`, `happy`, `n`, segment size, server count, server capacity, and failure modes, then inspect allocated shares and query counts.

The grid-backed `EncodingParameters` tests create a no-network Tahoe grid, upload data, directly manipulate stored share files, add or remove storage servers, mark servers read-only, corrupt or abort buckets, and re-run uploads. These tests encode many historical layouts from Tahoe tickets/comments and assert either successful redistribution to a happy layout or exact `UploadUnhappinessError` messages. The encoder drop tests separate selector-time failures from upload-time bucket loss. Bucket-abort tests wait for eventual abort messages and assert allocated storage returns to zero.

`StorageIndex` builds multiple `EncryptAnUploadable` instances to prove that convergence secret, encoding parameters, and random-key mode affect storage indexes as intended. `EncryptAnUploadableTests` read ciphertext in one piece or split pieces, including Hypothesis-generated split positions, and verify stable ciphertext length/result and chunked-read state.

## State And Persistence
Most state is in memory: fake server allocation lists, query counters, bucket writer contents, upload statuses, and client encoding parameters. Grid tests persist real share files under temporary no-network server directories, then mutate those files with `os.remove`, `shutil.copy`, and server add/remove operations. The module writes temporary upload source files for `FileName` tests and uses Tahoe node config files in `_set_up_nodes_extra_config` to verify persisted client encoding configuration.

## Dependencies And Integration Points
The module integrates `allmydata.immutable.upload`, `allmydata.immutable.encode`, `allmydata.uri`, `allmydata.monitor`, `allmydata.client`, `StorageFarmBroker`, storage-index directory layout, `GridTestMixin`, `ShouldFailMixin`, Twisted `Deferred`/`Clock` behavior, Foolscap-style `callRemote`, and Hypothesis. It is a regression harness for the upload selector, encoder, storage broker announcements, mutable read-only server discovery, and no-network grid share layout helpers.

## Risks And Test Signals
Strong signals include upload URI type selection, share-size limit enforcement, deterministic convergence encryption, distribution fairness, maximum contacted-server behavior, server error recovery, exact unhappiness diagnostics, read-only server accounting, existing-share discovery, query-count diagnostics, bucket abort cleanup, and ciphertext streaming invariants. The largest risks are brittleness from exact error-message assertions, historical permutation-dependent layouts, and direct filesystem share manipulation that depends on storage layout details. The fake server layer is intentionally partial and will not catch all real Foolscap/storage-server protocol changes.
