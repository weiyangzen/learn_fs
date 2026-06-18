# sources/storage-engines/wiredtiger/tools/wt_timestamps Research

## Purpose

`wt_timestamps` is a WiredTiger diagnostic CLI that prints global timestamp values for one or more WiredTiger home directories. By default it queries `all_durable`, `last_checkpoint`, `oldest`, `oldest_reader`, `pinned`, `recovery`, and `stable`, while allowing callers to request one or more specific timestamp categories with `-q`.

## Important APIs, Types, and Functions

`default_query` is the canonical list of timestamp query names used when no `-q` appears. `usage_exit()` prints accepted query names and exits. `wt_timestamps(conn, query)` opens a session and prints `<query>=<timestamp>` using `conn.query_timestamp('get=' + s)` for each requested item. The top-level script performs all argument parsing and directory iteration.

## Control Flow

The script consumes leading `-q <name>` pairs, requires at least one directory, substitutes `default_query` when the requested query list is empty, and then opens each directory read-only through `wiredtiger_open(arg, 'readonly')`. It prints a directory header, emits query results, closes the connection, and separates multiple directories with a blank line.

## State and Persistence Behavior

The tool opens read-only WiredTiger connections and does not mutate database state. It creates a session in `wt_timestamps()` but does not explicitly close it before closing the connection. Output is stdout-only. The module performs work at import time because parsing is top-level, so it is intended as an executable script rather than an importable library.

## Dependencies and Integration Points

It depends on `py_common.wiredtiger_util.wiredtiger_open` and the WiredTiger connection method `query_timestamp`. The query names must match what WiredTiger accepts in `query_timestamp('get=...')`; the comments document aliases intentionally omitted from the default list.

## Risks and Edge Cases

The usage line contains a typo, `wt_typestamp`, which can confuse users. Query values are not validated against `default_query`, despite the usage text implying a constrained set; invalid names are deferred to WiredTiger. The parser only accepts options while at least two arguments remain and the first begins with `-`, so a trailing malformed option can be treated as a directory. Importing the module will execute the CLI.

## Test Signals

Smoke tests should invoke the script against a temporary WiredTiger home and verify default labels, multiple directories, and repeated `-q` arguments. Negative tests should cover invalid query names, missing directory arguments, and readonly-open failures.
