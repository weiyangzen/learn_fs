# sources/storage-engines/wiredtiger/test/suite/test_chunkcache_cleanup.py

Purpose: verifies startup cleanup removes stale chunk cache metadata on connection reopen.

Important APIs and types: `WiredTigerTestCase`, metadata cursor `open_cursor("metadata:")`, `wiredtiger.WT_NOTFOUND`, and `reopen_conn`.

Control flow: create the historical chunk cache metadata file URI `file:WiredTigerCC.wt`, confirm it exists in metadata, reopen the connection, then search metadata again.

State and persistence behavior: the created metadata entry survives until close/reopen, at which point startup cleanup should delete it. This tests migration/deprecation cleanup rather than cache functionality.

Dependencies and integration points: integrates with connection startup metadata cleanup code and WiredTiger metadata cursor semantics.

Risks: only metadata removal is asserted; physical file cleanup is not separately checked. URI is hard-coded to the chunk cache file name.

Test signals: metadata search returns success before reopen and `WT_NOTFOUND` after reopen.
