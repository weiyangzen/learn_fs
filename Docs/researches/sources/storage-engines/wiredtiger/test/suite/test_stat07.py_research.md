<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat07.py

Purpose: validates session statistics cursor configuration compatibility and reset behavior.

Important APIs/types/functions: `test_stat_cursor_config` uses `SimpleDataSet`, `make_scenarios`, `session.open_cursor('statistics:session')`, `session.reset`, cursor `reset`, and `assertRaisesWithMessage`. Connection scenarios cover `statistics=none`, `fast`, and `all`; cursor scenarios cover empty, fast, and all.

Control flow: populate a small file dataset, build the cursor statistics config string, and either open a session stats cursor or assert the database statistics configuration rejects it. For valid combinations, call `session.reset`, reset the stats cursor, iterate all session stat values, and assert each value is zero while at least one stat was present.

State and persistence behavior: session statistics are per-session runtime counters and should be cleared by session reset plus cursor reset. No persistent data assertion beyond dataset population is required.

Dependencies/integration points: covers session stat URI, database statistics modes, config compatibility matrix, and session reset. Risks include expectations that every stat is zero after reset; signal is complete zeroed iteration or expected open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat07.py -->
