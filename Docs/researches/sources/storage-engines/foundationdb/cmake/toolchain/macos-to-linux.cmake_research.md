# sources/storage-engines/foundationdb/cmake/toolchain/macos-to-linux.cmake

## Purpose
CMake toolchain file for cross-compiling FoundationDB from macOS to x86_64 Linux with Swift/C++ interop.

## Important APIs, Types, and Functions
Sets `FOUNDATIONDB_CROSS_COMPILING`, Linux system name/processor, Swift/Clang/LLD/LLVM tools, Mono, Python3, sysroot, external GCC toolchain, C/C++ flags, Boost cross flags, and disables Mach-O search path behavior.

## Control Flow and Integration
CMake reads this before project configuration. It validates required toolchain roots and container root, wires compilers/linker/ar/ranlib, discovers host Python, and forces sysroot/target flags.

## State and Persistence
Depends on `FOUNDATIONDB_SWIFT_TOOLCHAIN_ROOT`, `FOUNDATIONDB_LLVM_TOOLCHAIN_ROOT`, `FOUNDATIONDB_LINUX_CONTAINER_ROOT`, Mono framework paths, and devtoolset-11 inside sysroot.

## Dependencies
State is forced CMake cache variables; no generated files here.

## Risks and Test Signals
Risks include hard-coded x86_64 target, hard-coded Mono/devtoolset paths, and host `which python3` variability. Test signal is a complete cross-configure and Swift stdlib rebuild.
