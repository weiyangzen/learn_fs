<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat06.py

Purpose: checks that statistics collection starts or remains disabled according to connection configuration, including interaction with statistics logging.

Important APIs/types/functions: `test_stat06` uses manual close/reopen with `wiredtiger_open`, `sleep`, `stat.conn.file_open`, and `assertRaisesWithMessage`. Default test config disables statistics.

Control flow: `test_stats_on` closes the default connection, opens with `statistics=(fast)`, creates two tables, waits, and confirms `statistics:` opens and reports file-open count. `test_stats_off` opens with `statistics=(none),statistics_log=(json)`, creates tables, waits, and expects opening `statistics:` to fail with a database statistics configuration error.

State and persistence behavior: statistics availability is connection-scoped runtime state; the test does not depend on table data beyond creating objects to affect file stats.

Dependencies/integration points: covers connection-level statistics config, statistics log config, cursor open admission, and background timing. Risks include sleep-based timing and exact error message coupling; signals are successful stats cursor read or expected cursor open failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat06.py -->
