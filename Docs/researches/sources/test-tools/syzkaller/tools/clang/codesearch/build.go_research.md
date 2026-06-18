<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/build.go -->
# sources/test-tools/syzkaller/tools/clang/codesearch/build.go

## Purpose

Linux-only cgo build shim for Clang-based syzkaller tools.

## Important APIs, Types, and Functions

cgo directives for C++23, warning suppressions, dynamic `-lclang-cpp -lclang -lLLVM`, and hard-coded LLVM 22/21/19 include/library paths.

## Control Flow

Imported for cgo side effects; build flags are applied when Go compiles the package, while runtime behavior lives in the C++ files selected by `SYZ_RUN_CLANGTOOL`.

## State and Persistence Behavior

No runtime state or persistence; build-time toolchain selection only.

## Dependencies and Integration Points

Requires Linux, cgo, a C++ compiler, and matching LLVM/Clang development libraries; dynamic linking preserves Clang plugin constructors.

## Risks and Edge Cases

Hard-coded distro paths and runtime shared-library lookup can fail on unsupported systems; build tag excludes non-Linux.

## Test Signals

Build and `go test` clangtool packages on supported LLVM versions and run a tiny ClangTool invocation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/build.go -->
