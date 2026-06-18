# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbdirectory.rb

Purpose: This file implements the Ruby FoundationDB directory layer, including high-contention prefix allocation, directory metadata management, directory subspaces, and partitions.

Important APIs and types: Core classes are `HighContentionAllocator`, `DirectoryLayer`, `DirectorySubspace`, `DirectoryPartition`, and `Internal::Node`. Public directory operations include `create_or_open`, `open`, `create`, `move`, `move_to`, `remove`, `remove_if_exists`, `list`, `exists?`, and subspace methods inherited from `Subspace`.

Control flow: Directory operations run inside `db_or_tr.transact`, check or initialize directory layer version metadata, locate nodes through subdir tables, allocate prefixes with the high-contention allocator when no manual prefix is supplied, validate prefix freedom, update parent subdirectory mappings, and recurse into partitions when needed. Removal recursively clears content and node metadata.

State and persistence behavior: Persistent state lives under node subspace `\xfe` by default and content prefixes allocated by the HCA. It stores version metadata, child-name to prefix mappings, layer strings, partition metadata, and user content ranges. Runtime state includes directory paths, layer names, allocator locks, and transaction-local allocator state.

Dependencies and integration points: It depends on `fdbimpl`, `fdbsubspace`, tuple packing, atomic add mutation, transaction conflict ranges, and Ruby binding transaction semantics. `FDB.directory` exposes a singleton default layer.

Risks: Directory metadata compatibility is version-sensitive. Manual prefixes can conflict with existing content if validation fails or is bypassed. Partition routing is subtle, especially for moves and root partition operations. HCA uses randomness and transaction-local locking to reduce conflicts.

Test signals: Ruby and Python directory tester extensions cover creation/opening, layers, manual prefixes, moves, recursive removal, partitions, list/existence, packing/unpacking, range behavior, logging, and expected error flattening.
