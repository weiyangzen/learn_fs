# sources/storage-engines/rocksdb/build_tools/ubuntu24_image/Dockerfile

## Purpose
This Dockerfile defines a RocksDB Ubuntu 24.04 build image and documents publishing it as `ghcr.io/facebook/rocksdb_ubuntu:24.1`. It tracks newer Ubuntu defaults, newer GCC, and an LLVM snapshot clang-21 path while keeping common RocksDB CI dependencies.

## Important APIs, functions, and control flow
The comments mirror the Ubuntu 22 image publishing workflow. The Docker build starts from `ubuntu:24.04`, updates/upgrades apt, installs basics plus ccache, timezone data, default GCC/G++/Clang tooling, then adds the LLVM snapshot apt key and `llvm-toolchain-noble-21` repository to install clang-21. It installs package helpers, gflags, TBB, compression libraries, CMake, OpenSSL, GCC/G++ 12 and 14, Valgrind, `libgoogle-glog-dev`, OpenJDK 8, MinGW, gtest-parallel, libprotobuf-mutator pinned to commit `ffd86a3...` using default clang/clang++, Google Benchmark v1.7.0, and removes apt lists.

## State, persistence, and dependencies
The image persists apt repository configuration under `/etc/apt`, LLVM GPG material under trusted keyrings, multiple compiler versions, Java configuration, `/root/gtest-parallel`, libprotobuf-mutator build artifacts, and `/usr/local` installs. It depends on Ubuntu Noble package availability, apt.llvm.org snapshot packages, GitHub source repositories, and GHCR for distribution.

## Integration points
It supports RocksDB testing on the newest supported Ubuntu baseline, including compiler matrix runs with GCC 12/14 and clang-21, fuzzing, benchmarks, Java builds, and MinGW targets. Because libprotobuf-mutator is built with default clang instead of a versioned clang, it follows the image default compiler state more closely than the 20/22 images.

## Risks and test signals
OpenJDK 8 on Ubuntu 24.04 can be availability-sensitive. The LLVM snapshot repository and clang-21 are moving external dependencies. `libgoogle-glog-dev` is packaged here, unlike the Ubuntu 22 source-build workaround, so folly/glog behavior can differ between images. Test by building the image, compiling RocksDB with GCC 12/14 and clang-21, running unit tests, building fuzzers and benchmarks, checking Java builds, and verifying Docker push instructions still match the intended GHCR tag.
