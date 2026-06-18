# sources/storage-engines/foundationdb/bindings/ruby/CMakeLists.txt

Purpose: This CMake file builds and packages the Ruby FoundationDB binding.

Important APIs and types: It uses `vexillographer_compile` to generate `lib/fdboptions.rb`, `configure_file` to produce `fdb.gemspec` and copy `LICENSE`, custom copy commands for Ruby source files, `ruby_binding` and `gem_package` targets, and the parent `packages` target dependency.

Control flow: CMake generates options, configures gem metadata, copies listed source files into the binary bindings tree, then builds a `.gem` with `GEM_COMMAND build` and copies it to the packages directory with a snapshot suffix when not a release.

State and persistence behavior: It writes generated option code in the source dir for debugging, copies binding files into the build dir, and writes package artifacts under `${CMAKE_BINARY_DIR}/packages`.

Dependencies and integration points: It depends on the FoundationDB CMake build, `GEM_COMMAND`, generated option metadata, package target conventions, and the Ruby source file list.

Risks: The source list must stay synchronized with gemspec file lists and actual library files. Generating into the source directory can dirty worktrees. Snapshot naming depends on `FDB_RELEASE`.

Test signals: A successful build should produce copied Ruby library files, generated `fdboptions.rb`, configured gemspec, and a gem package target that participates in `packages`.
