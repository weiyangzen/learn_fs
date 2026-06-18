# sources/storage-engines/wiredtiger/test/csuite/normalized_pos/main.c

Purpose: white-box correctness test for WiredTiger normalized page positions (`npos`). It verifies that pages can be traversed in normalized-position order and that an `npos` computed from a page maps back to the expected page for both eviction and read lookup paths.

Important APIs, types, and functions: the test includes `wt_internal.h` and uses internal types `WT_SESSION_IMPL`, `WT_CURSOR_BTREE`, `WT_DATA_HANDLE`, and `WT_REF`. `create_btree` creates `table:normalized_pos` with small 1KB page sizing and inserts 100,000 fixed-size values. `test_normalized_pos` accepts either `__wt_page_from_npos_for_eviction` or `__wt_page_from_npos_for_read`, calls `__wt_page_npos`, releases refs with `__wt_page_release`, and uses `WT_WITH_DHANDLE`. `run` executes both in-memory and on-disk variants.

Control flow: `run` creates a working home, opens WiredTiger either in-memory with 1GB cache or on-disk with 1MB cache, builds the btree, then runs the normalized-position test for eviction and read. `test_normalized_pos` first searches all keys to stabilize the tree, walks forward from `npos=0` and backward from `npos=1` using page-from-npos callbacks, checks monotonic npos movement, optionally checks exact page count and no duplicate refs in memory, then searches every key, computes the page's midpoint npos and optional path string, checks monotonicity across keys, maps the npos back to a page, and verifies exact ref equality in memory.

State and persistence behavior: creates and deletes `WT_TEST.normalized_pos`. In-memory mode keeps the page shape simple and stable; on-disk mode permits less exact page counts because disk layout can pack pages differently. The test manipulates hazard references and releases them explicitly.

Dependencies and integration points: depends on internal WiredTiger page tree functions and structures, not public API stability. Registered as `test_normalized_pos` and normally launched through `normalized_pos/smoke.sh`.

Risks: tightly coupled to internal Btree/page-ref behavior. The comments note the one-key-per-page expectation is not always exact. Any change in page split/layout, hazard pointer discipline, or normalized-position algorithm may require adjusted assertions. Because it uses internal headers, it is not a portable external test.

Test signals: in-memory runs should traverse exactly `NUM_KEYS` pages forward and backward and map every key page back exactly. On-disk runs should preserve monotonic order and forward/backward count equality for read lookup where asserted.
