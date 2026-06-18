<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_split.py -->
# sources/storage-engines/wiredtiger/test/suite/test_split.py

Purpose: checks that reconciliation creates expected leaf page splits for a simple row-store file as records are appended and inserted.

Important APIs/types/functions: `test_split` uses `WiredTigerTestCase`, `stat.dsrc.btree_row_leaf`, `session.create`, cursors, and repeated `reopen_conn` calls. Connection config enables all statistics.

Control flow: create a file with 4KB allocation and leaf pages plus `split_pct=75`, insert 35 records sized to fit one leaf page, reopen and assert one row leaf page, append 10 records enough to exceed the page target, reopen and assert two leaf pages, then insert five records in the key gap and confirm the leaf-page count remains two.

State and persistence behavior: each `reopen_conn` stabilizes the table by closing and reopening, forcing reconciliation and durable page layout. The assertions depend on physical page sizes, not only logical contents.

Dependencies/integration points: integrates reconciliation split policy, file-store page sizing, statistics, and connection reopen. Risks are explicitly noted: changes in reconciliation page sizing can legitimately alter expected counts. Test signals are exact `btree_row_leaf` values after each phase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_split.py -->
