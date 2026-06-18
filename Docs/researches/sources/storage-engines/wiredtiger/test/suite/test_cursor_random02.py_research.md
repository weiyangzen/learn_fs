# sources/storage-engines/wiredtiger/test/suite/test_cursor_random02.py

Purpose: verifies that `next_random=true` cursors over an insert-list-heavy table return a reasonable spread of keys and do not simply walk in key order. It scenarios table type with record counts from 1 through 50000.

Important APIs and control flow: `SimpleDataSet.populate()` creates `table:random` with `leaf_page_max=100MB` to avoid page splits. The test opens `session.open_cursor(uri, None, 'next_random=true')`, calls `cursor.next()` once per record, records `cursor.get_key()`, and tracks adjacent sequential returns.

State and persistence: all state is in one populated WiredTiger table and in Python counters (`visitedKeys`, `sequentialKeys`). No restart is involved; the page layout choice is part of the test signal.

Dependencies and integration: depends on `wttest`, `SimpleDataSet`, and `make_scenarios`. It targets the random cursor implementation for insert-list contents.

Risks and test signals: statistical assertions are intentionally loose: more than one quarter of keys must be seen and a multi-row table must not be entirely sequential. Failures indicate broken random distribution or unexpected ordered traversal.
