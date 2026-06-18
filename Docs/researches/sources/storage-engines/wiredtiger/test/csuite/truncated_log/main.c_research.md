# sources/storage-engines/wiredtiger/test/csuite/truncated_log/main.c

Purpose: this test validates recovery from a log file truncated in the middle of a log record. It constructs a database that has crossed into log file 2, truncates `WiredTigerLog.0000000001` inside its final record, opens with recovery, verifies that only valid records remain, and checks that a new log record can be written and read after recovery.

Important APIs, types, and functions: it uses `WT_LSN`, log cursors (`"log:"`), `WT_CURSOR`, `WT_SESSION`, process `fork`/`waitpid`, POSIX `truncate`, and WiredTiger logging configuration. `fill_db` creates the initial database and records the last log file 1 offset plus maximum key. `write_and_read_new` writes a `log_printf` message, flushes it, and walks the log cursor. `main` orchestrates child creation, truncation, recovery, verification, and cleanup.

Control flow: the child `fill_db` opens WiredTiger with small 100K log files and no sync, creates `table:main`, inserts keys until the log cursor sees records in log file 2, and writes the saved log file 1 offset and key marker into `records`. The parent reads that marker, truncates log file 1 at `offset + V_SIZE`, opens WiredTiger with recovery enabled, counts table records, then invokes `write_and_read_new`.

State and persistence behavior: the test directly mutates log persistence by truncating a WiredTiger log file after the child exits. It expects recovery to stop at the partial record, discard later invalid log records including ordinary records from log file 2, and then continue logging in a later file. The table may be row-store or column-store via `-c`.

Dependencies and integration points: it uses common test utility parsing and cleanup, a local work directory `WT_TEST.truncated-log`, and `statistics_log` for diagnostics. The smoke wrapper runs both row and column variants.

Risks and test signals: risks include incorrect offset selection, platforms with different truncate behavior, and log cursor traversal accidentally accepting invalid log file 2 records. Passing requires recovered record count not exceeding the expected valid prefix and the post-recovery log message being visible through a log cursor.
