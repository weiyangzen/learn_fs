<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_different_encoding.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_different_encoding.py

Purpose: Verifies that a mutable file created with one total-share encoding can later be modified by a client configured with a different encoding.

Important APIs and functions: `DifferentEncoding` builds `FakeStorage` and a nodemaker. `test_filenode` modifies `default_encoding_parameters["n"]`, creates a mutable file, reconstructs it from its cap after disabling object reuse, changes `n` again, and calls `modify`.

Control flow: The test creates a 3-of-20 file, discards the original node object, creates a new node from the cap with 3-of-10 defaults, and performs a modifier that replaces the contents.

State and persistence: Uses in-memory fake storage and mutable nodemaker defaults. No filesystem state.

Dependencies and integration points: Depends on `.util.FakeStorage`, `.util.make_nodemaker`, `AsyncTestCase`, and mutable filenode modification logic.

Risks: The test targets historical issue behavior where clients latched to incompatible encoding assumptions. It does not assert downloaded contents, only that modification completes.

Test signals: A successful Deferred is the primary signal; failure would indicate servermap/publisher assumptions tied too strongly to the creator's encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_different_encoding.py -->
