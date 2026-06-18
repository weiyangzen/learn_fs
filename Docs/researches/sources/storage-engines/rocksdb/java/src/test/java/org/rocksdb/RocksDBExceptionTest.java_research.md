# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RocksDBExceptionTest.java

## Purpose

This file tests how native RocksDB status failures are surfaced as Java `RocksDBException` instances. It verifies message generation and optional `Status` fields for plain messages, status codes, subcodes, and native state strings.

## Important APIs and types

The suite uses `RocksDBException`, `Status`, `Status.Code`, and `Status.SubCode`. Six private native methods intentionally throw exceptions through JNI to cover different status/message combinations.

## Control flow

Each test invokes one native method, catches `RocksDBException`, checks status presence and field values, then returns. If no exception is thrown, the test fails. Message fallback is covered when native code supplies a status without an explicit message.

## State and persistence behavior

No database state is created. The important state is exception payload transfer across JNI: status code, subcode, optional state bytes/string, and Java message text must survive native-to-Java conversion.

## Dependencies and integration points

`@BeforeClass` calls `RocksDB.loadLibrary()`, so the test depends on native test symbols being linked into the RocksDB JNI library. It is a direct contract test for exception construction helpers in the native Java binding.

## Risks and test signals

Risks include losing `Status` metadata, incorrectly defaulting subcodes, exposing null messages, or changing fallback message formatting. Signals are exact assertions on status code, subcode, state nullability, and message text.
