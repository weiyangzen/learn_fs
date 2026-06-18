# sources/storage-engines/wiredtiger/test/suite/test_unicode01.py

## Purpose
`test_unicode01.py` is a smoke test that WiredTiger metadata configuration accepts Unicode text.

## Important APIs, Types, and Functions
The class defines `test_unicode` and calls `session.create('table:t', metadata_string)` with a metadata string containing Unicode characters.

## Control Flow
The test builds a metadata/config string and creates a table. There are no reads or additional assertions; failure would occur during create/config parsing.

## State and Persistence Behavior
The created table's metadata is persisted in WiredTiger metadata files. Unicode content must survive config parsing and metadata storage.

## Dependencies and Integration Points
Depends on `wttest`, Python Unicode string handling, and WiredTiger metadata/config parsing.

## Risks and Edge Cases
This is minimal coverage: it only tests acceptance, not dump/reopen behavior or exact metadata round-tripping.

## Test Signals
The table create call completes without raising a `WiredTigerError`.
