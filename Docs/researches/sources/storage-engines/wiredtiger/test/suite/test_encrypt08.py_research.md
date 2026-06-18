# sources/storage-engines/wiredtiger/test/suite/test_encrypt08.py

## Purpose

Covers system-level libsodium encryption configuration errors, especially invalid or unsupported key specifications passed to the encryptor customize method.

## Important APIs, Types, and Functions

Defines `test_encrypt08`, sodium test key constant, `encrypt_type` scenarios for missing key, key id, duplicate key specs, non-hex key, and wrong key length, plus `conn_extensions` and `test_encrypt`.

## Control Flow

The harness initially opens without encryption so exceptions can be caught explicitly. Each scenario reopens with `encryption=(name=sodium,<bad config>)` and asserts a `WiredTigerError` matching the expected sodium diagnostic.

## State and Persistence Behavior

There is no table data; persistence behavior is limited to connection reopen behavior and extension initialization state.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wttest`, `make_scenarios`, and the optional `sodium` encryptor extension. It targets connection-level encryption parsing and extension customization.

## Risks and Maintenance Signals

The test assumes sodium is available or skipped by extension loading. It intentionally avoids `conn_config`; if WiredTiger later rejects reopen-with-different-encryption earlier, the test setup may need an overridden open path.

## Test Signals

Signals are scenario-specific exception regexes for no key, key IDs unsupported, duplicate key mechanisms, non-hex secrets, and wrong key length.
