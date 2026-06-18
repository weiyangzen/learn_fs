# sources/user-network-fs/go-fuse/all.bash

Purpose: central CI/test driver for go-fuse. It prints kernel information, verifies builds, runs tests, root-only tests, virtiofs tests, benchmark builds, and benchmark runs.

Important flow: `set -eux`; `go build ./...`; cross-builds key packages for Darwin and FreeBSD; sets `GO_TEST="go test -timeout 5m -p 1 -count 1"` to expose hangs, serialize output, and avoid cache; runs all tests as current user; runs selected `DirectMount`, `Forget`, `Passthrough`, and `IDMappedMount` tests with sudo; runs virtiofs tests with shorter timeout; builds benchmark C/Go helpers and executes benchmarks with CPU 1,2.

Dependencies/integration: requires Go, FUSE permissions, sudo, benchmark toolchain, optional QEMU/KVM behavior in virtiofs. Risks include tests that need root or kernel capabilities and external tools such as `make`, `g++`, `pkg-config fuse`. Test signal is broad and intentionally includes GOMAXPROCS-sensitive behavior via CI.
