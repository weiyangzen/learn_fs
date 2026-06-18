<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_interoperability.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_interoperability.py

Purpose: Verifies that the current mutable downloader can read legacy SDMF shares.

Important APIs and data: `Interoperability` embeds ten base64-encoded old SDMF shares, an old SSK cap, and expected contents. `copy_sdmf_shares` writes decoded shares into a no-network grid's server share directories. `test_new_downloader_can_read_old_shares` downloads through a modern nodemaker-created node.

Control flow: The test sets up a grid, maps old shares to ten server numbers, computes the storage index from the cap, writes each share to `shares/<storage_index_dir>/<share>`, confirms all shares are found, constructs a node from the old cap, and downloads the best version.

State and persistence: Writes fixture shares into test server directories under the grid basedir. Class-level fixture bytes are static.

Dependencies and integration points: Uses `GridTestMixin`, `AsyncTestCase`, `ShouldFailMixin`, Tahoe URI parsing, storage index path mapping, file utilities, and no-network grid helpers.

Risks: Large inline fixtures are hard to review and easy to corrupt. The test assumes ten servers and direct on-disk storage layout compatibility. It validates one legacy fixture rather than a full migration matrix.

Test signals: All ten fixture shares are discoverable and `download_best_version` returns `b"This is a test file.\n"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_interoperability.py -->
