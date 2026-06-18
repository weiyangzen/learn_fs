# sources/object-store/minio-mc/cmd/share-db-v1.go

## Purpose
Defines the version 1 local JSON database used to persist generated share upload/download URLs.

## Important APIs, types, and functions
- `shareEntryV1` records original object URL, version ID, creation date, expiry duration, and optional content type.
- `shareDBV1` stores DB version, a mutex, and a map keyed by share URL.
- `newShareDBV1` initializes version `1`, the map, and mutex.
- `Set` inserts or replaces a share entry keyed by `shareURL`.
- `Delete` removes a map entry by key, despite the parameter being named `objectURL`.
- `deleteAllExpired` removes expired entries.
- `Load` loads from disk with `quick`, copies entries, prunes expired shares, and saves the pruned DB.
- `save` and `Save` persist through `quick.NewConfig`.

## Control flow
Callers create a DB with `newShareDBV1`, call `Load(filename)`, mutate entries with `Set`/`Delete`, then call `Save(filename)`. `Load` checks file existence, loads using the MinIO `quick` config layer, copies loaded shares into the current DB, prunes expired entries, and writes the cleaned DB back to disk.

## State and persistence
Persists JSON files in the share config directory, normally `uploads.json` and `downloads.json`. Mutexes protect in-process map access, but there is no inter-process file lock.

## Dependencies and integration points
Used by share upload/download/list commands. Depends on `github.com/minio/pkg/v3/quick`, Go `maps.Copy`, `os.Stat`, and `UTCNow`.

## Risks and edge cases
- No cross-process locking, so concurrent `mc share` processes can race and lose updates.
- `Delete(objectURL string)` deletes by map key, which is actually share URL; the parameter name can mislead callers.
- `Load` ignores loaded `Version` except through the target structure; migrations are handled elsewhere.
- `deleteAllExpired` mutates the map without taking a lock itself, but current callers invoke it under the `Load` lock.

## Test signals
No direct tests in this subset. Tests should cover load/save round trips, expired entry pruning and rewrite, Set/Delete key semantics, and concurrent in-process access.
