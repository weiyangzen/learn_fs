# sources/storage-engines/wiredtiger/test/suite/helpers/helper.py

Purpose: general Python suite helper functions for file/table comparison, URI existence checks, WiredTiger home copying, crash-restart simulation, statistics URI construction, and cursor context management.

Important APIs and control flow: `compare_files()` performs byte-for-byte size and buffer comparison. `compare_tables()` opens multiple cursors and checks value equality while scanning in lockstep. `confirm_does_not_exist`, `confirm_empty`, and `confirm_nonempty` assert URI visibility and backing-file patterns. `copy_wiredtiger_home()` copies a home while skipping lock/temp log files and can use unaligned `dd`. `simulate_crash_restart()` copies an open home, closes the old connection, and reopens on the copy. `WiredTigerCursor` implements `with` support around `session.open_cursor`.

State and persistence behavior: can create/copy/remove directories, copy WiredTiger files, run `dd`, close and reopen test connections, and leave copied homes for inspection.

Dependencies and integration points: depends on `wiredtiger`, `shutil`, `subprocess`, filesystem globbing, and `wttest`-style testcase methods. Many suite tests import these helpers directly.

Risks: `compare_tables()` compares cursor values rather than keys and can miss key divergence if values match. Unaligned copy uses `dd` and is unavailable on Windows. Copying a live home is a crash simulation, not a true power-loss test.

Test signals: helper assertions make absence/emptiness/comparison failures explicit in downstream tests.
