# sources/storage-engines/wiredtiger/test/suite/test_debug_mode10.py

Purpose: smoke tests `debug_mode=(realloc_malloc=true)`, an allocation debug mode that exercises malloc-style reallocation behavior.

Important APIs and control flow: `insert_data` creates `file:test_debug_mode10`, writes one string record, closes the cursor, and checkpoints. `test_realloc_exact` runs with the mode enabled; `test_realloc_exact_off` reconfigures with `debug_mode=(realloc_malloc=false)` and repeats.

State and persistence: the checkpoint is intentionally included because reconciliation and checkpoint code invoke reallocation paths repeatedly.

Dependencies and integration: uses `wttest`, cursor item assignment, `session.checkpoint`, and `conn.reconfigure`.

Risks and test signals: like other allocator debug tests, it does not inspect allocator internals. It catches errors, crashes, or inability to reconfigure while preserving normal file-table behavior.
