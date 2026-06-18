<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/old-env/Dockerfile -->
# sources/test-tools/syzkaller/tools/docker/old-env/Dockerfile

## Purpose

Legacy Ubuntu-based syzkaller environment image.

## Important APIs, Types, and Functions

Ubuntu 20.04, cross compilers, Go 1.22.7, clang-12 from apt.llvm xenial, precreated syz-env dirs.

## Control Flow

Installs packages layer-by-layer, downloads Go, adds LLVM repo/key, installs clang-12, symlinks clang, prepares writable dirs.

## State and Persistence Behavior

State baked into image only.

## Dependencies and Integration Points

Depends on old Ubuntu/LLVM/Go repos and Docker.

## Risks and Edge Cases

Old repos/tools can disappear or contain CVEs; apt-key is deprecated; may not match current repo needs.

## Test Signals

Build and run representative old-branch bisection/build commands.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/old-env/Dockerfile -->
