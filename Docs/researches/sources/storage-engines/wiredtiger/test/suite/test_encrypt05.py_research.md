# sources/storage-engines/wiredtiger/test/suite/test_encrypt05.py

## Purpose

Validates that encryption configuration parsing rejects quoted escaped control characters embedded in key ids instead of silently accepting malformed encryption material.

## Important APIs, Types, and Functions

Defines `test_encrypt05`, the `escaped_characters` scenario list for newline, carriage return, tab, and backspace, `conn_extensions`, `conn_config`, and `test_encrypt`.

## Control Flow

The default connection opens with valid `rotn` encryption. Each scenario builds a malformed `encryption=(name=rotn,keyid="11<escaped>")` config and calls `reopen_conn`. A `WiredTigerError` is expected to mention invalid argument; afterward the test reopens with an empty config to avoid teardown using the intentionally bad configuration.

## State and Persistence Behavior

No user data is persisted. State is the connection configuration under test and the harness stderr ignore rule for the parser diagnostic.

## Dependencies and Integration Points

Uses the `wiredtiger` Python API, `wttest`, `make_scenarios`, and the `rotn` encryptor extension. It targets the WiredTiger configuration parser and encryption customization path.

## Risks and Maintenance Signals

The test only asserts when an exception is raised; if malformed input ever succeeds, the body does not explicitly fail before the valid reopen. The diagnostic text is partially normalized through stderr ignores, so wording changes may need updates.

## Test Signals

Signals are exception type, presence of `Invalid argument`, and teardown safety via a clean reopen.
