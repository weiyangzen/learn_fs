<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/index.go

This file defines `Index`, a map from index name to a set of keys. It supports `AddToIndex`, `RemoveFromIndex`, `GetKeys`, and `IsKeyInIndex`.

The structure is used by simple snapshot metadata stores to associate snapshot IDs or metadata keys with logical indexes. Control flow is straightforward set mutation: initialize a nested map on first add, delete keys from an index, return keys as an unordered slice, and check membership.

State is in-memory and JSON-serializable through map types when embedded in persisted metadata. Risks include nondeterministic key order from `GetKeys`, nil map panic if methods are called on a nil `Index` without initialization, and no automatic cleanup of empty index maps. Direct unit tests cover add/remove/get/membership behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index.go -->
