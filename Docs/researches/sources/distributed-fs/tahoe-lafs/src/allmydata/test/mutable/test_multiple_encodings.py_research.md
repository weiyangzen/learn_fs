<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_encodings.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_encodings.py

Purpose: Tests retrieval behavior when shares for the same mutable file exist with multiple encoding parameters.

Important APIs and functions: `MultipleEncodings` uses `FakeStorage`, `make_nodemaker`, `MutableData`, `Publish`, `ServerMap`, `ServermapUpdater`, `MODE_READ`, and `DevNullDictionary`. `_encode(k, n, data, version)` publishes a temporary representation with custom required/total shares and returns captured peer shares.

Control flow: Setup creates an initial file in fake storage. `_encode` disables node cache, reconstructs from cap, copies key fields, changes `_required_shares`/`_total_shares`, clears storage, publishes, captures shares, and clears storage again. `test_multiple_encodings` creates 3-of-10, 4-of-9, and 4-of-7 share sets, manually merges chosen share numbers from each set into storage, fixes server query order, then downloads from a fresh node.

State and persistence: Mutates fake storage `_peers` and `_sequence`, nodemaker `_node_cache`, and temporary filenode internals. No filesystem state.

Dependencies and integration points: Exercises mutable publisher, servermap updater, retrieval version selection, storage broker server IDs, and fake storage ordering.

Risks: Directly copying private filenode fields and storage internals makes the setup fragile. The expected behavior is "first version recoverable", so a future policy change for multi-version retrieval would need test updates.

Test signals: Download should return the 3-of-10 contents once that version becomes recoverable despite earlier shares from incompatible encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_encodings.py -->
