# sources/storage-engines/wiredtiger/test/suite/test_encrypt09.py

## Purpose

Covers per-table libsodium encryption configuration errors and documents how table encryption differs from system encryption, especially around unsupported `secretkey` table options.

## Important APIs, Types, and Functions

Defines `test_encrypt09`, sodium key constant, per-file `encrypt_type` scenarios, `conn_extensions`, `conn_config`, and `test_encrypt`.

## Control Flow

The connection opens with valid system sodium encryption. The test attempts to create a file object with `encryption=(name=sodium,<scenario>)`. The no-key case succeeds because no separate encryptor is generated; keyid is rejected by sodium; `secretkey` scenarios fail earlier as unknown per-table configuration.

## State and Persistence Behavior

State is object-creation metadata only. Successful no-key creation persists a file object using inherited system encryption behavior.

## Dependencies and Integration Points

Depends on the `wiredtiger` API, `wttest`, scenario generation, and the sodium extension. It integrates system encryption setup with object-level create configuration.

## Risks and Maintenance Signals

Several expected failures are parser-level, not extension-level, by current design. If per-table secret keys become supported, the expected errors and coverage intent will change.

## Test Signals

Signals are successful create for no-key and regex-matched `WiredTigerError` failures for unsupported key id and per-table secretkey attempts.
