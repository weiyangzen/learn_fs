# sources/storage-engines/foundationdb/bindings/ruby/fdb.gemspec.in

Purpose: This is a Ruby gemspec input with placeholder version text for the FoundationDB Ruby binding.

Important APIs and types: It mirrors the configured gemspec fields but uses `VERSION` instead of the CMake `${FDB_VERSION}` variable.

Control flow: Packaging or release tooling can substitute the placeholder before building a gem. Runtime code does not read this file.

State and persistence behavior: It only controls package metadata and included files.

Dependencies and integration points: It must remain aligned with `fdb.gemspec.cmake`, `CMakeLists.txt`, Ruby source file names, and the dependency on `ffi`.

Risks: Divergence between `.in` and `.cmake` variants can create inconsistent package metadata. The fixed file list can omit new library files if not maintained.

Test signals: Gem build validation should confirm version substitution and complete file inclusion.
