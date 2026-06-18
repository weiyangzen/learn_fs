# sources/storage-engines/wiredtiger/tools/wt_cmp_uri.py Research

## Purpose

`wt_cmp_uri.py` is a WiredTiger diagnostic CLI for comparing the key/value contents of two WiredTiger URIs, usually in two separate home directories. It can also compare the same home at different read timestamps, which is useful for validating timestamp visibility, checkpoint snapshots, and test/format mirror-table output. The tool exits with status `0` when the cursor streams match and `1` when it finds missing keys, value differences, EOF mismatches, or cursor/opening errors.

## Important APIs, Types, and Functions

The main entry point is `wiredtiger_compare_uri(args)`, called from `__main__`. It parses `-v` and one or two `-t` timestamp options, splits each positional argument with `get_dir_uri()`, opens WiredTiger connections with `py_common.wiredtiger_util.wiredtiger_open`, and obtains `CompareCursor` wrappers through `get_compare_cursor()`.

`CompareCursor` encapsulates a WiredTiger cursor, URI/name metadata, a detected `reverse` collation flag, and an `at_end` latch. Its `cursor_next()` method normalizes cursor iteration: once `WT_NOTFOUND` is observed, all future calls return `WT_NOTFOUND`, and unexpected WT errors are converted to a diagnostic plus `sys.exit(1)`. `wt_open()` opens a session, optionally begins a transaction at `read_timestamp=<timestamp>`, and opens a readonly cursor. `is_reverse()` reads the `metadata:` cursor for a URI and detects `collator=reverse`, which is a test/format-specific custom collation case. `compare_cursors()` is the core merge-walk comparison algorithm. `compare_version_cursors()` is an unfinished deeper version-cursor comparator; the main path deliberately passes `False` for version comparison.

## Control Flow

Argument parsing first consumes a leading `-v` and optional first timestamp, then requires `dir1/uri1`, optionally accepts a second timestamp before `dir2/uri2`, and rejects extra arguments. `wiredtiger_compare_uri()` opens one or two readonly connections; if both home directories are equal it reuses the first connection so same-home timestamp comparisons do not attempt a second open.

`compare_cursors()` advances cursor 1, then cursor 2, compares keys, and performs a sorted merge. If keys differ, it advances the side with the smaller key, adjusted for the `reverse` collator, and prints missing-key diagnostics with throttling after ten consecutive missing entries. Equal keys lead to value comparison. At the end, it checks whether cursor 2 still has records after cursor 1 is exhausted. Record counts are printed on exit paths.

## State and Persistence Behavior

The tool is read-only against WiredTiger data. It creates sessions and cursors, may begin read transactions for timestamp reads, and closes cursors, sessions, and connections explicitly. Its only persistent side effect is process output. Global state is limited to `verboseFlag`.

## Dependencies and Integration Points

This script requires the Python WiredTiger bindings, `WT_NOTFOUND`, `wiredtiger_strerror`, and the repository helper `py_common.wiredtiger_util.wiredtiger_open`. `validate_mirror_tables.py` imports `wiredtiger_compare_uri`, so the function-level entry point is part of internal test tooling. The metadata cursor ties comparison behavior to WiredTiger object metadata and collator configuration.

## Risks and Edge Cases

`get_dir_uri()` uses the last slash and will throw if an argument lacks `/`; malformed inputs are mostly handled by usage checks but not by path-specific validation. `is_reverse()` assumes the URI exists in metadata and that metadata is readable. The version-cursor branch is not currently used and has constructor calls missing the `reverse` argument, so enabling it would fail without repair. Generic `except:` blocks around cursor open print context but re-raise without narrowing error types. Custom collators other than the detected reverse collator are not supported; if two objects have equal-looking keys but incompatible ordering, merge recovery can misreport differences.

## Test Signals

Useful tests include matching and intentionally divergent tables, EOF mismatches, reverse-collator tables from test/format, same-home comparisons at two timestamps, and invalid URI/path arguments. A regression test should also cover imported `wiredtiger_compare_uri()` usage because callers depend on the function exiting with the comparison status.
