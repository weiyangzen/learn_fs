<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor06.py

Purpose: tests runtime cursor `reconfigure()` for `overwrite` and read-only behavior across file/table, row/column, and complex datasets.

Important APIs and control flow: scenarios combine URI type, key/value format, and `SimpleDataSet` or `ComplexDataSet`. `test_reconfigure_overwrite()` repeatedly toggles `overwrite=0` and `overwrite=1`, asserting duplicate insert failure then success. `test_reconfigure_readonly()` verifies updates fail for cursors opened read-only and succeed otherwise. `test_reconfigure_invalid()` checks invalid reconfiguration keys produce `Invalid argument`.

State, persistence, and dependencies: persistent state is populated dataset content reused under different cursor configs. Dependencies are `wiredtiger`, datasets, `dropUntilSuccess`, cursor `reconfigure`, and hook skips for timestamp.

Integration points: covers cursor-level configuration mutability after open and its interaction with insert/update semantics.

Risks and test signals: dropping/recreating objects across scenarios must avoid stale handles. Pass signals are duplicate-key enforcement under overwrite false, write rejection under read-only, and invalid config rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor06.py -->
