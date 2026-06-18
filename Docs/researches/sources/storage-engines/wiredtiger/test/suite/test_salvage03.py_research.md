<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_salvage03.py

Purpose: tests salvage behavior when key metadata or data files are removed from a copied WiredTiger home, distinguishing files that should still open, files salvage can repair, and files known not to be salvageable.

Important APIs/types/functions: `test_salvage03` extends `WiredTigerTestCase` and `suite_subprocess`; it uses `helper.copy_wiredtiger_home`, `databaseCorrupted`, `reopen_conn`, scenario sets for `WiredTiger`, `WiredTiger.basecfg`, `WiredTiger.turtle`, `WiredTiger.wt`, `WiredTigerHS.wt`, and `test_salvage03.wt`, plus row and column key formats.

Control flow: create and populate a table, copy the live home to `RESTART`, close, remove one selected file, copy that corrupted directory to `RESTART2`, and try both normal and salvage opens depending on the scenario. For salvageable cases it opens with `cache_size=1GB,salvage=true`; for known bad cases it expects `WiredTigerError`.

State and persistence behavior: persistence is modeled by directory copies taken before clean close, then metadata/data loss on the copy. The test checks whether recovery plus salvage can rebuild enough metadata and file state to open.

Dependencies/integration points: integrates metadata files, turtle/base config handling, history store absence, table file absence, row/column formats, and skip hooks for tiered storage. Risks include intentionally broad error regexes and a skipped turtle anomaly; signals are successful salvage opens or expected open failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage03.py -->
