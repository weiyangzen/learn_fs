# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor01.py

## Purpose
Basic smoke test for metadata cursor iteration and search over `metadata:` and `metadata:create`.

## APIs, Types, And Functions
Defines `test_metadata_cursor01` with scenarios for plain and create metadata cursors. Helpers generate keys/values, assert cursor key/value are unset, and wrap `Session.create` for better diagnostics.

## Control Flow, State, And Persistence
Each test creates a simple table, opens the selected metadata cursor, and verifies cursor state before iteration. Forward and backward tests iterate until `WT_NOTFOUND` and ensure keys and values are available while positioned. The search test fetches `metadata:` itself and the created table entry, checking for `key_format` in metadata strings. Metadata state is persisted in the WiredTiger metadata table.

## Dependencies, Integration, Risks, And Test Signals
Depends on metadata cursor URI variants and standard cursor reset semantics. Risks are invalid positioned/unpositioned cursor state, incomplete create metadata expansion, or missing table metadata. Signals are key/value availability checks, final `WT_NOTFOUND`, and substring checks in metadata values.
