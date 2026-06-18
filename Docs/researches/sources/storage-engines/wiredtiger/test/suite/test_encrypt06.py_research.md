# sources/storage-engines/wiredtiger/test/suite/test_encrypt06.py

## Purpose

Checks that enabled encryption does not leave table data, key names, value names, column group content, or index content visible as clear text in WiredTiger files.

## Important APIs, Types, and Functions

Defines `test_encrypt06` with scenario products over storage layouts and encryptor configurations. Important helpers are `conn_extensions`, `conn_config`, `encrypt_table_params`, `match_string_in_file`, `match_string_in_rundir`, `visible_data`, and `visible_name`.

## Control Flow

For each scenario it creates two tables with named key/value columns, optional column groups, and optional indexes. It inserts patterned keys and values, closes the connection to force files to disk, then scans every run-directory file for known plaintext strings. Matched scenarios assert visibility exactly from table/system encryption settings; unmatched child object scenarios apply conservative no-leak checks.

## State and Persistence Behavior

Persistence is tested by raw file inspection after close. The test intentionally searches both data payload markers and schema-name markers, accounting for metadata/system encryption and the special case where column groups move key names out of data files.

## Dependencies and Integration Points

Depends on `os`, `wttest`, `make_scenarios`, `rotn`, optional `sodium`, table/colgroup/index creation, connection-level encryption, and per-object encryption configuration. It is skipped for tiered storage.

## Risks and Maintenance Signals

Raw substring scans can produce false positives if unrelated files contain the marker strings, though the markers are distinctive. Unmatched child-object behavior documents a current conservative expectation rather than the full theoretical API semantics.

## Test Signals

Signals are absence or presence of plaintext markers in on-disk files across system, table, index, and column-group encryption combinations, including sodium system encryption.
