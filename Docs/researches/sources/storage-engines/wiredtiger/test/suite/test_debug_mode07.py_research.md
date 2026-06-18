# sources/storage-engines/wiredtiger/test/suite/test_debug_mode07.py

Purpose: smoke tests `debug_mode=(realloc_exact=true)` from WT-4919 and confirms it can be turned off.

Important APIs and control flow: `insert_data` creates `file:test_debug_mode07`, writes one string key/value, closes the cursor, and checkpoints. One test runs under the initial debug config; the other calls `conn.reconfigure('debug_mode=(realloc_exact=false)')` before the same workload.

State and persistence: a single record and checkpoint exercise allocation and reconciliation paths where `realloc` is frequently used.

Dependencies and integration: uses `wttest`, session create/open cursor/checkpoint, and connection reconfiguration.

Risks and test signals: there is no direct allocator introspection, so passing means the mode does not break ordinary operation. It is primarily a crash/assertion guard for exact reallocation debug behavior.
