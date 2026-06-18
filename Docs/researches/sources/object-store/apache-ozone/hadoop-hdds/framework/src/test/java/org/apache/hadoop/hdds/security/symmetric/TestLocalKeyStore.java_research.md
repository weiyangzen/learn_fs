# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestLocalKeyStore.java

## Purpose

This class tests `LocalSecretKeyStore` JSON persistence, file permissions, overwrite semantics, and backward-compatible loading of existing key-store schema.

## Important APIs, Types, And Functions

It uses `SecretKeyStore.save`, `load`, `LocalSecretKeyStore`, `ManagedSecretKey`, JCA `KeyGenerator`, `SecretKeySpec`, Base64 decoding, and POSIX file permission checks.

## Control Flow

Setup creates a temp JSON file and store. Parameterized save/load tests cover empty, single, and multiple keys. `testOverwrite()` saves one list then another. `testLoadExistingFile()` writes a literal historical JSON payload and compares the loaded key fields.

## State And Persistence

State is persisted in the temp JSON file. Saved files must exist and have owner read/write permissions only. Key fields include UUID, creation/expiry time, algorithm, and encoded secret key bytes.

## Dependencies And Integration Points

The test integrates Guava collection helpers, Java NIO permissions, JCA crypto, and the symmetric key persistence layer used by secret-key managers.

## Risks

POSIX permission checks can fail on non-POSIX filesystems. The existing-file JSON is a backward-compatibility fixture and should not be changed casually.

## Test Signals

Signals include exact reloaded key fields, secure file permissions, overwrite replacing prior keys, and successful load of the hard-coded historical JSON.
