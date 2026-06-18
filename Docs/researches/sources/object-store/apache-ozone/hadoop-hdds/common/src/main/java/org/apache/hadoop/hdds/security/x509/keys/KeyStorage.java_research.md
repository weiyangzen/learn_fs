# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/KeyStorage.java

## Purpose
Persists and reads component key pairs in PEM format with strict POSIX permissions, while also supporting externally supplied root CA keys.

## Important APIs and types
Constructors resolve key paths from `SecurityConfig` and component name, optional suffix, or an internal path. `readPrivateKey`, `readPublicKey`, and `readKeyPair` decode existing PEM files. `storePrivateKey`, `storePublicKey`, and `storeKeyPair` encode and write keys. Permission constants are `rwx------` for directories and `rw-------` for key files.

## Control flow and state
During construction, if `SecurityConfig.useExternalCACertificate(component)` is true, paths are taken from external root CA config and must be readable; store operations later throw `UnsupportedOperationException`. Otherwise the key directory is created or sanitized to owner-only permissions, and key file paths are resolved from configured names. Store creates a new file with owner-only permissions then writes encoded bytes.

## Dependencies and integration points
Depends on `SecurityConfig`, `KeyCodec`, Java NIO files, POSIX file permissions, and Java key classes. Certificate clients, root CA setup, and rotation managers use it for local and staged key material.

## Risks and test signals
Tests should cover new directory creation, existing directory permission reset, read/write round trips, external key read paths, unreadable external path failures, store rejection for external keys, and behavior when target files already exist. Because `Files.createFile` fails if the file exists, overwrite/rotation behavior must be explicitly handled by callers.
