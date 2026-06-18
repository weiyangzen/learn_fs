# sources/storage-engines/tikv/Dockerfile

## Purpose
This Dockerfile builds a TiKV release image by compiling TiKV in a Rocky Linux builder and copying `tikv-server` and `tikv-ctl` into a runtime base image.

## Important APIs, types, and functions
It has three stages: `builder` from Rocky Linux 8.10 UBI, `building` that copies the source and runs `ROCKSDB_SYS_STATIC=1 make dist_release`, and final image from `ghcr.io/pingcap-qe/bases/tikv-base:v1.9.2`. It installs compiler/build tools, Go, OpenSSL development headers, CMake dependencies, protobuf `protoc`, and rustup.

## Control flow
The builder stage upgrades packages and installs dependencies, downloads architecture-specific protobuf compiler artifacts, and installs rustup without a default toolchain. The building stage compiles release binaries and verifies `tikv-server --version`. The final stage sets `MALLOC_CONF`, copies binaries to `/tikv-server` and `/tikv-ctl`, exposes ports 20160/20180, and sets `/tikv-server` as entrypoint.

## State and persistence behavior
The build creates Cargo/target artifacts in a cached mount and final image layers containing only runtime base plus two binaries. Runtime persistent data is external to this Dockerfile.

## Dependencies and integration points
It depends on public base images, DNF repositories, GitHub protobuf releases, rustup, TiKV Makefile release targets, and the PingCAP QE runtime base image.

## Risks and edge cases
The header notes the file may be outdated versus PingCAP QE artifacts. Network downloads and package repo availability affect reproducibility. Rust toolchain selection is delegated to repository configuration/Makefile. Static RocksDB and release builds are resource-intensive.

## Test signals
Docker build success, `/tikv/bin` copy success during build, `tikv-server --version`, final container startup, exposed service/status ports, and `tikv-ctl` presence validate this file.
