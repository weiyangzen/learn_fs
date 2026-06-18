# sources/storage-engines/wiredtiger/test/suite/test_util18.py

## Purpose

`test_util18.py` tests `wt printlog` formatting, redaction, hexadecimal output, messages-only output, and LSN-range filtering under logging-enabled connections.

## Important APIs, Types, and Functions

The class uses scenario flag `print_user_data`, `conn_config`, `populate`, and `check_populated_printlog`. Test methods cover default printlog, `-x`, `-m`, and `-l` range behavior. It uses log cursors and `session.log_printf`.

## Control Flow

Each test creates/populates a table, optionally writes a log message, runs `wt printlog` with option combinations, and asserts whether JSON key/value fields or hex fields appear. The LSN test derives first, second, and last LSNs from a `log:` cursor and compares bounded outputs.

## State and Persistence Behavior

The test requires retained log files (`log=(enabled,file_max=100K,remove=false)`). It persists small key/value updates, log messages, and printlog output files for comparison.

## Dependencies and Integration Points

Integrates WiredTiger logging, log cursors, `wt printlog`, redaction policy controlled by `-u`, and output formatting.

## Risks and Edge Cases

The LSN cursor loop calls `c.next()` inside the loop body, which can skip records; the test still extracts a last LSN but depends on available log records. Output assertions are sensitive to JSON field spelling.

## Test Signals

Signals include expected user-data redaction, hex emission only when requested and unredacted, message-only suppression of data records, and equivalence between explicit first LSN and `1,0` range starts.
