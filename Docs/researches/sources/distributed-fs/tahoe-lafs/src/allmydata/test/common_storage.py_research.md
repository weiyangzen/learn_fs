<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_storage.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_storage.py

Purpose: Supplies tiny synchronous helpers for directly placing immutable and mutable shares into a `StorageServer` during tests.

Important APIs and functions: `upload_immutable(storage_server, storage_index, renew_secret, cancel_secret, shares)` allocates buckets and writes each immutable share. `upload_mutable(storage_server, storage_index, secrets, shares)` builds test/write vectors and invokes mutable slot write APIs.

Control flow: Immutable uploads call `allocate_buckets`, then write each returned writer at offset zero and close it. Mutable uploads convert each share into `(test_vectors, write_vectors, new_length)` format and call `slot_testv_and_readv_and_writev` with an empty read vector.

State and persistence: The helpers persist share data into the supplied storage server's backing store. They do not track cleanup or leases beyond the arguments passed to the storage APIs.

Dependencies and integration points: Depends on the `StorageServer` immutable bucket API and mutable slot vector API. Used by tests that need pre-arranged storage state without going through full publisher code.

Risks: `upload_immutable` assumes all shares have the same length and uses the first value as the allocation size. Existing `already` buckets are ignored, so tests must supply fresh or intentionally overwrite-compatible inputs. Mutable writes perform no validation beyond whatever the storage server enforces.

Test signals: Exercise empty and multi-share maps, pre-existing shares, mismatched immutable share lengths, mutable test-vector failures, and expected lease/secret behavior in storage tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_storage.py -->
