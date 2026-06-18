# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStateImpl.java

## Purpose
`SecretKeyStateImpl` is the default in-memory and persisted implementation of `SecretKeyState`.

## Important APIs, Types, And Functions
It uses a `ReadWriteLock` to guard `sortedKeys`, `currentKey`, and `keyById`. `getCurrentKey()`, `getKey(UUID)`, and `getSortedKeys()` acquire the read lock. `updateKeys()` and `reinitialize()` call `updateKeysInternal()`, which sorts keys newest-first, sets the current key, builds the UUID map, and saves to `SecretKeyStore`.

## Control Flow
Updates acquire the write lock, replace all derived views atomically, persist the sorted list, then release. Reads return current field references under the read lock. `getKey()` returns null if the state has not been initialized.

## State, Persistence, And Dependencies
State is in-memory key views plus the backing `SecretKeyStore`. Persistence happens on every update/reinitialize via `keyStore.save(sortedKeys)`. Dependencies include locks, stream collectors, and logging.

## Integration Points
`SecretKeyManager` owns lifecycle decisions but delegates actual state updates and persistence here. In production, this object is expected to be behind SCM replication proxying for annotated updates.

## Risks
`getSortedKeys()` can return null before initialization. `updateKeysInternal()` assumes `newKeys` is non-empty; otherwise `sortedKeys.get(0)` fails. Returned `sortedKeys` is immutable but key objects contain key material.

## Test Signals
Tests should verify initial null behavior, update ordering, current key selection, UUID lookup, persistence calls, reinitialize behavior, empty-list failure, and concurrent read/write safety.
