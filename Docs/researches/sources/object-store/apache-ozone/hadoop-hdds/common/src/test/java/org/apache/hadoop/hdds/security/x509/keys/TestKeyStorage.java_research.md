# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyStorage.java

## Purpose
Tests `KeyStorage` behavior for internal and external CA key storage, including read/write round trips, permissions, overwrite protection, and failure paths.

## Important APIs, types, and functions
- Uses `KeyStorage`, `KeyCodec`, `SecurityConfig`, RSA `KeyPair`, `PrivateKey`, `PublicKey`, and POSIX permission constants `DIR_PERMISSIONS` and `FILE_PERMISSIONS`.
- Internal-CA nested tests cover `storeKeyPair`, `storePrivateKey`, `storePublicKey`, `readPrivateKey`, `readPublicKey`, `readKeyPair`, suffixed storage paths, codec failures, IO failures, overwrite rejection, and initialization failures.
- External-CA nested tests cover reading configured external key paths and rejecting writes.
- Uses Mockito to simulate `FileSystemProvider`, `FileSystem`, `Path`, and codec exceptions.

## Control flow
A static RSA key pair is generated once. Each test configures mocked `SecurityConfig` paths and codec behavior. Internal storage tests write keys to a temp directory, assert files and permissions, decode file contents, and read through `KeyStorage`. Failure tests replace codec or filesystem behavior to force exceptions. External storage tests pre-create key files and verify read-only access.

## State and persistence behavior
This file actively writes temporary key files and validates filesystem permissions. It models production key persistence under component-specific security directories and external CA key paths.

## Dependencies and integration points
`KeyStorage` is part of HDDS security bootstrap and CA/key management. It integrates `SecurityConfig`, filesystem permissions, key encoding, and external CA configuration.

## Risks and test signals
Risks include overwriting private keys, writing with weak permissions, failing to read external CA keys, and obscuring IO/codec errors. The suite gives strong signals for key-file durability, read-only external CA semantics, and permission enforcement.
