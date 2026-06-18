# sources/sync-backup/syncthing/internal/db/typed_test.go

## Purpose
This test file validates the typed KV wrapper against the SQLite KV backend.

## Important APIs and Control Flow
`TestNamespacedInt` opens a temporary SQLite DB, constructs two `Typed` wrappers with prefixes `foo` and `bar`, and runs parallel subtests. The `Int` subtest verifies missing-key behavior, put/read, namespace isolation, and delete. The `Time` subtest verifies missing zero time and binary time round trip. The `String` subtest verifies missing empty string and string round trip.

## State and Persistence Behavior
The test writes to the SQLite common `kv` table through prefixed keys. It proves deleting a typed key removes only that prefixed key and that namespaces do not collide.

## Dependencies and Integration Points
The test imports `internal/db` and `internal/db/sqlite`, so it exercises the generic wrapper and the concrete SQLite `KV` implementation together.

## Risks and Test Signals
Parallel subtests share one database and different keys, so they provide light concurrency coverage. Missing direct coverage for bytes, bool, corrupt values, and `NewMiscDB` remains.
