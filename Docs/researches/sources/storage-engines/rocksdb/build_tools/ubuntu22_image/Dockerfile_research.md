# sources/storage-engines/rocksdb/build_tools/ubuntu22_image/Dockerfile

## Purpose
This Dockerfile defines a publishable RocksDB Ubuntu 22.04 build image, with inline instructions for building and pushing `ghcr.io/facebook/rocksdb_ubuntu:22.2`. It modernizes compiler coverage while preserving clang-13/fuzzer compatibility.

## Important APIs, functions, and control flow
The comment header documents GHCR login, build, push, and visibility steps. The Docker body starts from `ubuntu:22.04`, updates and upgrades apt, installs `vim`, `wget`, `curl`, `ccache`, timezone data, compilers, package helpers, gflags/TBB/compression/CMake/OpenSSL. It installs clang-13 through `llvm.sh`, installs `libc++-13-dev` and `libc++abi-13-dev`, then purges clang-14 to avoid libc++/libstdc++ confusion with C++20. It installs GCC 10 and GCC 13 from the toolchain PPA, Valgrind, and builds glog v0.7.1 from source because the packaged dependency path lacks compatible libunwind. It adds OpenJDK 8, MinGW, gtest-parallel, libprotobuf-mutator pinned to commit `ffd86a3...` built with clang-13, and Google Benchmark v1.7.0, then removes apt lists.

## State, persistence, and dependencies
Persistent image state includes the compiler matrix, ccache, source-built glog in `/usr/local`, gtest-parallel under `/root`, libprotobuf-mutator/protobuf build artifacts, benchmark install files, and Java/protobuf environment variables. Network dependencies include Docker Hub base image pulls, apt.llvm.org, Ubuntu archives, the toolchain PPA, GitHub, and GHCR for publication.

## Integration points
The image is an official-ish RocksDB CI image used by build scripts and human release workflows. It integrates with C++20 clang/libc++ testing, GCC version testing, fuzzers, benchmark builds, Java builds, and cross-compile checks.

## Risks and test signals
Risks include hand-built glog needing `-DGLOG_USE_GLOG_EXPORT` in consumers, fragility of OpenJDK 8 availability on Jammy, unpinned package updates, and stale image tag instructions if GHCR naming changes. Test by building the image from `build_tools/ubuntu22_image`, compiling RocksDB under GCC 10/13 and clang-13 with libc++, running representative unit tests, building fuzzers and benchmark targets, and verifying glog-dependent folly paths link.
