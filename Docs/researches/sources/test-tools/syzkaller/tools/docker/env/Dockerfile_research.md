<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/env/Dockerfile -->
# sources/test-tools/syzkaller/tools/docker/env/Dockerfile

## Purpose

Current syzkaller development/test Docker environment.

## Important APIs, Types, and Functions

Multi-stage Debian trixie image: prebuilt Fuchsia/NetBSD toolchains, custom Git, Go 1.26, LLVM 22, cross compilers, fs tools, Spanner emulator, Rust, node, gcloud.

## Control Flow

Downloads/install packages and archives, configures alternatives, GOPATH/GOMODCACHE/source dirs, gcloud components, writable dirs for host UID, and bash entrypoint.

## State and Persistence Behavior

Container filesystem stores toolchains/SDKs/cache dirs; runtime persistence comes from mounts.

## Dependencies and Integration Points

Depends on Debian, apt.llvm.org, storage.googleapis.com, Go/Rust/gcloud downloads, Docker networking.

## Risks and Edge Cases

Many pinned remote downloads and `trusted=yes` LLVM repo increase reproducibility/supply-chain risk; image is large.

## Test Signals

Build image, run presubmit subsets, cross-compile executor, dashboard/gcloud tests, verify tool versions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/env/Dockerfile -->
