# sources/sync-backup/borg/src/borg/testsuite/hashindex_test.py

Purpose: tests `ChunkIndex` entry insertion, pack-location updates, missing-key behavior, struct bounds, and tracking of newly added entries.

Important APIs and control flow: helpers `H` and `H2` generate deterministic 32-byte keys. `test_chunkindex_add` adds a chunk with unknown pack location, allows size fill-in from zero, rejects inconsistent size updates, and checks `ChunkIndexEntry` fields. `test_chunkindex_update_pack_info` updates multiple chunks with pack id, offsets, and object sizes, then confirms `None` and empty updates are no-ops. `test_keyerror` checks missing lookup and oversize struct packing. `test_new` exercises `iteritems(only_new=True)` and `clear_new`.

State and persistence: in-memory hash index only. The "new" bitset/state is mutable and explicitly cleared.

Dependencies and integration points: depends on `borg.hashindex.ChunkIndex`, `ChunkIndexEntry`, and sentinel constants `UNKNOWN_INT32`/`UNKNOWN_BYTES32`. It supports cache and repository object-location bookkeeping.

Risks: C-extension struct limits can surface as `struct.error`; field widths and flag names are part of the compatibility contract.

Test signals: exact entry equality, no-op update behavior, expected exceptions, and new-entry iterator state.
