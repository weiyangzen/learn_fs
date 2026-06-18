<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_partition.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_partition.go

Purpose: adapts a nested `directoryLayer` as a directory partition. A partition is a directory object but deliberately not a usable key subspace at its root.

Important APIs: `directoryPartition` embeds `directoryLayer` and stores `parentDirectoryLayer`. It implements subspace methods (`Sub`, `Bytes`, `Pack`, `PackWithVersionstamp`, `Unpack`, `Contains`, `FDBKey`, `FDBRangeKeys`, `FDBRangeKeySelectors`) by panicking, returns layer bytes `partition`, and routes `MoveTo`, `Remove`, and `Exists` to either the parent or nested layer via `getLayerForPath`.

Control flow: empty relative path operations refer to the partition directory in the parent layer; non-empty paths refer to the nested layer. `MoveTo` uses the common `moveTo` helper against the parent path. `Remove` and `Exists` compute partition-relative paths with `partitionSubpath`.

State and persistence: this file does not write state directly. It controls which `directoryLayer` writes metadata and content for partition-root versus partition-child operations.

Dependencies and integration: depends on `fdb`, `subspace`, `tuple`, and helpers from `directory_layer.go`. It is created by `contentsOfNode` when a node layer equals `partition`.

Risks: panic-based rejection means callers must not treat partition roots as normal subspaces. Incorrect path routing would delete/check the wrong layer. Type assertions in callers assume partition values satisfy `DirectorySubspace` but not normal subspace behavior.

Test signals: should be covered by directory partition tests: root subspace method panics, partition-child operations delegate inside partition, and root removal/existence uses the parent layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_partition.go -->
