## sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.cpp

Purpose: implements directory handles that are also usable as subspaces, forwarding directory operations relative to the stored directory path.

Important APIs and functions: constructor initializes `Subspace(prefix)`, `directoryLayer`, `path`, and `layer`. `create`, `open`, `createOrOpen`, `exists`, `list`, `move`, `moveTo`, `remove`, and `removeIfExists` delegate to an appropriate `DirectoryLayer` using `getPartitionSubpath`. Accessors return layer/path/directory layer.

Control flow: relative operations calculate a partition-relative subpath by stripping the owning directory layer path from `this->path` and appending the requested path. `moveTo` verifies the destination absolute path remains inside the same directory layer partition before calling layer `move`.

State and persistence: no direct metadata writes; all persistence is delegated to `DirectoryLayer`. The object stores immutable path/layer identity and raw prefix through `Subspace`.

Dependencies and integration points: used as the returned handle from directory open/create and as the base for `DirectoryPartition`.

Risks: incorrect `directoryLayer->getPath()` sizes or path prefix comparisons can produce wrong relative paths. `getDirectoryLayerForPath` is virtual so partitions alter delegation behavior.

Test signals: directory tester operations on currently selected directory/subspace exercise these relative forwarding methods.
