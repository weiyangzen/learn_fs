# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeleteKeysResult.java

## Purpose

`DeleteKeysResult` is a small result holder used by `DirectoryDeletingService`-related flows to return keys selected for deletion and whether keys were processed.

## Important APIs and Types

- Constructor accepts `List<OmKeyInfo> keysToDelete` and `boolean processedKeys`.
- `getKeysToDelete()` returns the key list.
- `isProcessedKeys()` returns the processing flag.

## Control Flow

There is no behavior beyond construction and getters.

## State and Persistence

The object holds in-memory result state only. It does not persist data; downstream deletion services decide how to move/purge OM metadata.

## Dependencies and Integration Points

It depends on `OmKeyInfo` and is referenced by `DirectoryDeletingService` and `KeyManager` methods for pending deletion subdirectories/subfiles.

## Risks and Edge Cases

The fields are mutable and not final, though there are no setters. The key list is returned directly, so callers can mutate it. The meaning of `processedKeys` requires external contract knowledge.

## Test Signals

Tests are likely indirect through directory deletion service behavior; direct tests would assert constructor/getter values and caller handling of empty lists or false processing state.
