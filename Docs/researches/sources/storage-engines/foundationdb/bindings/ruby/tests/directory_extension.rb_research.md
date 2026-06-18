# sources/storage-engines/foundationdb/bindings/ruby/tests/directory_extension.rb

Purpose: This is the Ruby binding tester adapter for directory-layer and subspace instructions.

Important APIs and types: `DirectoryExtension::DirectoryTester` maintains a directory handle list, active index, and error index. It processes directory create/open/move/remove/list/exists, subspace creation/opening, pack/unpack/range/contains, logging, and prefix stripping instructions.

Control flow: Each instruction pops values from the tester stack using `wait_and_pop`, invokes the current directory/subspace object, pushes normalized results, and appends new handles for operations that create or open directories. Exceptions append `nil` for create-like operations and push `DIRECTORY_ERROR`.

State and persistence behavior: Runtime state is the directory handle table. Persistent state is mutated through `FDB::DirectoryLayer` operations and log writes requested by the instruction stream.

Dependencies and integration points: It depends on `fdb`, `FDB::Tuple`, `FDB::Subspace`, `FDB::DirectoryLayer`, and the `Instruction` protocol in `ruby/tests/tester.rb`. It mirrors Python's directory extension for conformance testing.

Risks: Stack pop order, tuple path conversion, and error normalization must match the tester spec exactly. Throwing versus raising in prefix-strip failure is a minor Ruby-specific behavior to watch.

Test signals: Directory instruction streams validate Ruby directory semantics against other bindings, including manual prefixes, partitions, moves, removals, listing, key conversion, and error cases.
