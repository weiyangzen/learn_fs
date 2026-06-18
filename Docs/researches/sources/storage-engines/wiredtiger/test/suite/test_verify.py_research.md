# sources/storage-engines/wiredtiger/test/suite/test_verify.py

## Purpose

`test_verify.py` is broad coverage for `wt verify` and `WT_SESSION.verify`, including empty/populated tables, corrupt pages, truncation, redaction, and verifying all tables.

## Important APIs, Types, and Functions

Helpers include `file_name`, `populate`, `check_populate`, `count_file_contains`, `open_and_position`, and `open_and_offset`. Test methods cover process/API success paths, checksum corruption at offsets/percentages, `read_corrupt`, dump-address diagnostics, zero-length/truncated files, redacted dump-pages output, and `verify -a`.

## Control Flow

Positive tests create tables, populate data, and verify through subprocess or API. Corruption tests close the connection via helper, overwrite or truncate table files, reopen when needed, run verify with diagnostic options, and inspect stdout/stderr. The redaction test inserts secret values, checkpoints, compares redacted and `-u` unredacted output.

## State and Persistence Behavior

This file directly mutates WiredTiger data files after closing the connection, so disk state is central. It relies on no checkpoints before initial object-name assumptions and uses checkpointing for redaction/all-table scenarios.

## Dependencies and Integration Points

Depends on filesystem access to `.wt` or tiered object names, `suite_subprocess`, diagnostic build gating, `helper.WiredTigerCursor`, API verify, utility verify, checksum reporting, and stderr/stdout pattern filtering.

## Risks and Edge Cases

Several corruption helpers are skipped for disaggregated storage. Offset selection may hit free space or parent pages, so assertions allow at least one checksum error rather than exact full coverage.

## Test Signals

Signals include successful verify on clean data, expected `WT_SESSION.verify` errors on corruption, dump-address read-failure messages, checksum diagnostics, no secret data in redacted output, secret data with `-u`, and abort behavior that stops after the first corrupted table.
