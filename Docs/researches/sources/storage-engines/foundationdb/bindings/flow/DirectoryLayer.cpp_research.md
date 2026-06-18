## sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.cpp

Purpose: implements the Flow binding directory layer, including directory metadata storage, prefix allocation, creation/opening, listing, moving, recursive removal, partition delegation, and version compatibility checks.

Important APIs and functions: static metadata keys define node/content layout. `find` walks path components through subdirectory mapping keys. `checkVersionInternal` validates or initializes metadata version. `getPrefix`, `nodeContainingKey`, and `isPrefixFree` allocate or validate content prefixes. `createInternal`, `_createOrOpenInternal`, `listInternal`, `moveInternal`, `removeRecursive`, `removeInternal`, and `existsInternal` implement the main asynchronous behavior.

Control flow: public methods wrap `this` in `Reference<DirectoryLayer>` and delegate to actor-style helper functions. Creation checks version, validates manual prefix policy, finds existing nodes, delegates into partitions when needed, allocates/free-checks a prefix, writes parent subdir mapping and node layer metadata, then returns a `DirectorySubspace` or `DirectoryPartition`. List/remove operations page through ranges until `more` is false.

State and persistence: stores version at `rootNode.pack(VERSION_KEY)`, subdirectory mappings under `SUB_DIR_KEY`, node layer at `LAYER_KEY`, allocator state under `hca`, and user content under allocated prefixes. Removes clear both content prefix ranges and node metadata ranges.

Dependencies and integration points: uses `Subspace`, `Tuple`, `HighContentionAllocator`, `DirectorySubspace`, `DirectoryPartition`, Flow actors, and `Transaction` wrapper range/read/write APIs.

Risks: correctness depends on tuple/key range boundaries, prefix-free checks, and partition path arithmetic. Metadata version is read as `uint32_t*`, so endian/alignment assumptions matter. Manual prefix policy differs for root versus partitions.

Test signals: exercised by `DirectoryTester.cpp` instruction functions and by cross-binding directory layer compatibility tests.
