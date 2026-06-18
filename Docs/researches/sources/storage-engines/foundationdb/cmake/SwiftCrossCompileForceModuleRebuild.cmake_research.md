# sources/storage-engines/foundationdb/cmake/SwiftCrossCompileForceModuleRebuild.cmake

## Purpose
Forces Swift builtin modules to rebuild from `.swiftinterface` files during cross-compilation.

## Important APIs, Types, and Functions
Defines `swift_force_import_rebuild_of_stdlib()`.

## Control Flow and Integration
The function rewrites `CMAKE_Swift_FLAGS` into frontend-safe flags, adds strict implicit module context, compiles tiny `import Swift` and `import CxxStdlib` Swift files, and fails if either import/rebuild fails.

## State and Persistence
Depends on Swift compiler, correct resource-dir/sysroot flags, and cross-compile toolchain setup from `ConfigureCompiler.cmake`/toolchain file.

## Dependencies
Temporary Swift source/object files persist under `CMakeTmp`; no project outputs are installed.

## Risks and Test Signals
Risks include brittle flag tokenization on spaces and strict module rebuild failures with mismatched host/target Swift versions. Test signal is configure-time successful import of Swift and CxxStdlib.
