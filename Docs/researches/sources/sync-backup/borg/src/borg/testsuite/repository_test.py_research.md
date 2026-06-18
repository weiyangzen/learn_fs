# sources/sync-backup/borg/src/borg/testsuite/repository_test.py

## Purpose
Regression tests for Borg repository storage, pack writing, chunk index persistence, REST serve command construction, partial reads, object listing, consistency, max object size, and failure rollback behavior. It locks down how `Repository` and `PackWriter` store and retrieve raw `RepoObj`-formatted chunks.

## Important APIs, Types, and Functions
Helpers include `reopen`, `fchunk`, `pchunk`, `pdchunk`, `check`, `MockStore`, and `FailingPackStore`. Tests call `Repository.put/get/delete/list/check/store_store`, `PackWriter.add/flush`, `ChunkIndex.add/update_pack_info`, cache functions, and `rest_serve_command`.

## Control Flow
Fixtures create repositories, insert synthetic raw chunks, close/reopen to verify persisted indexes, and manually inject pack/index entries for range reads. Pack writer tests cover non-full flushes, N=1 pack IDs, N=2 SHA256 pack IDs, final partial pack hashing, and rollback when storage fails.

## State and Persistence Behavior
Persistent state includes pack blobs under `packs/`, cached chunk index fragments, repository object membership, and object deletion records. The failure tests ensure in-memory and serialized chunk indexes do not retain phantom entries for packs that failed to store.

## Dependencies and Integration Points
The file integrates repository storage, cache serialization, hash index entries, REST-local/SSH command generation, binary object framing from `RepoObj`, and chunk index pack routing.

## Risks and Test Signals
Risks include stale/phantom dedup indexes causing data loss, off-by-one pack range reads, oversized data acceptance, and inconsistent list pagination. Test signals are object not found after delete/reopen, exact pack offsets/sizes, cache fragment membership, no temp files after check, and clean rollback on simulated pack-store failures.
