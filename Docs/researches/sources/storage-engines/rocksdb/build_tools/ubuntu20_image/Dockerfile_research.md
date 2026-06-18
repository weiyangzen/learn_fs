# sources/storage-engines/rocksdb/build_tools/ubuntu20_image/Dockerfile

## Purpose
This Dockerfile defines a RocksDB CI/build image based on Ubuntu 20.04. It installs compilers, compression libraries, Java, MinGW, gtest-parallel, libprotobuf-mutator, and Google Benchmark for regular builds, sanitizer/fuzzer workflows, benchmark builds, and cross-platform checks.

## Important APIs, functions, and control flow
The image is built through Docker `RUN` layers. It updates and upgrades apt packages, installs basic tools, configures `tzdata` noninteractively, installs default GCC/G++/Clang tooling, package management helpers, `libgflags-dev`, `libtbb-dev`, compression dev packages, `cmake`, and `libssl-dev`. It downloads `llvm.sh` from apt.llvm.org and installs clang-13, installs GCC 7, 8, 10, and 11 through the Ubuntu toolchain PPA, installs Valgrind, `libgoogle-glog-dev`, OpenJDK 8 with `JAVA_HOME`, and MinGW. It clones `google/gtest-parallel` onto `PATH`, then builds `google/libprotobuf-mutator` at branch `v1.0` pinned to commit `ffd86a3...` with clang-13 and Ninja, exposes `PKG_CONFIG_PATH` and `PROTOC_BIN`, builds Google Benchmark v1.7.0, and removes apt lists and the benchmark source checkout.

## State, persistence, and dependencies
Persistent image state includes apt packages, LLVM/GCC toolchains, `/root/gtest-parallel`, `/root/libprotobuf-mutator`, `/usr/local` installs for libprotobuf-mutator and benchmark, and environment variables for Java, `PATH`, protobuf pkg-config, and `protoc`. It depends heavily on external apt repositories, GitHub, the Ubuntu toolchain PPA, and apt.llvm.org.

## Integration points
The image supports RocksDB's make/CMake builds, gtest-parallel test execution, fuzzers needing libprotobuf-mutator and bundled protobuf, benchmark targets needing Google Benchmark, Java API builds, Valgrind checks, and MinGW compilation.

## Risks and test signals
Risks include unpinned package upgrades, branch `master` for gtest-parallel, reliance on old OpenJDK 8 packages, and no apt cache cleanup until the end, which enlarges intermediate layers. The PPA and LLVM installer are external trust and availability points. Test by building the image, compiling RocksDB with default GCC and clang-13, running gtest-parallel, building fuzzers against `PROTOC_BIN`, and linking benchmark targets.
