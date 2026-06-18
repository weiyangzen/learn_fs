# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/LocalSecretKeyStore.java

## Purpose
`LocalSecretKeyStore` persists managed symmetric secret keys to a local JSON file so SCM can reload valid keys across restarts.

## Important APIs, Types, And Functions
The constructor takes a file path and configures Jackson with Java time support and ISO date serialization. `load()` returns an empty list if the file is absent, otherwise deserializes `ManagedSecretKeyDto` entries. `save(Collection)` creates the file/directories, maps keys to DTOs, and writes all entries with `SequenceWriter`. `ManagedSecretKeyDto` stores UUID, creation/expiry times, algorithm, and encoded key bytes.

## Control Flow
`save()` calls `createSecretKeyFiles()`, which creates parent directories/file when needed and sets owner read/write POSIX permissions. Load and save are synchronized.

## State, Persistence, And Dependencies
State is the target path and object mapper. Persistence is the JSON secret-key file with `OWNER_READ` and `OWNER_WRITE` permissions. Dependencies include Jackson, Java crypto key specs, Java NIO file APIs, and POSIX permissions.

## Integration Points
`SecretKeyStateImpl` calls `save()` whenever replicated key state changes, and `SecretKeyManager` calls `load()` during initialization.

## Risks
POSIX permissions may fail on non-POSIX filesystems. Writes are not atomic, so interruption can corrupt the file. The JSON contains raw encoded secret keys and relies on filesystem permissions for protection. Deserialization errors throw `IllegalStateException`.

## Test Signals
Tests should cover absent file loads, round-trip serialization, permission setting, parent directory creation, malformed file behavior, synchronization under concurrent calls, and non-POSIX platform behavior.
