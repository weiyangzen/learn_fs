<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_layer.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_layer.go

Purpose: implements the Go directory layer root and core operations for creating, opening, listing, moving, and deleting directory paths. `directoryLayer` binds a metadata subspace (`nodeSS`), content allocation subspace (`contentSS`), high-contention allocator, root node, manual-prefix policy, and current partition path.

Important APIs: `NewDirectoryLayer`, `CreateOrOpen`, `Create`, `CreatePrefix`, `Open`, `Exists`, `List`, `Move`, `Remove`, plus helpers `find`, `contentsOfNode`, `checkVersion`, `isPrefixFree`, `nodeContainingKey`, and recursive removal helpers. `createOrOpen` is the central state machine: check layer version, reject illegal manual prefixes/root opens, resolve existing nodes, delegate into partitions, validate layer bytes, allocate or validate prefixes, ensure parents, then persist parent `_SUBDIRS` and node `layer` keys.

State and persistence: directory metadata is stored under `nodeSS`, with root metadata at `rootNode`, child name to prefix mappings under `_SUBDIRS`, per-node layer bytes under `node/<prefix>/layer`, and directory version under root `version`. Directory contents live at the allocated prefix itself. Removing clears both metadata and the content prefix range.

Dependencies and integration: relies on `fdb.Transactor`/`ReadTransactor`, `subspace`, `tuple`, `highContentionAllocator`, and partition/subspace wrappers. Partitions are represented by layer string `partition` and create nested directory layers whose metadata is under `prefix + 0xFE`.

Risks: many helpers use `MustGet`, so asynchronous FDB errors become panics recovered only when called inside transaction helpers. Prefix allocation correctness depends on both `isRangeEmpty` and `isPrefixFree`; manual prefixes can create conflicts if policy checks drift. Recursive delete can be large and transaction-size sensitive. `find` stops at partition boundaries, so path math must remain exact.

Test signals: no direct test in this subset, but integration is exercised by directory-layer users elsewhere. Risk areas need partition delegation, move/delete recursion, incompatible directory-version, and manual-prefix conflict coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory_layer.go -->
