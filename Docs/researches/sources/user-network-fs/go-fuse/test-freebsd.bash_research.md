<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/test-freebsd.bash -->
# sources/user-network-fs/go-fuse/test-freebsd.bash

## Purpose
Automates FreeBSD test execution for go-fuse inside a QEMU VM backed by a downloaded FreeBSD raw image.

## Important APIs, Types, and Functions
The bash script downloads/caches an image, copies it, attaches it via loop, mounts UFS with `fuse-ufs-bin`, cross-compiles Go test binaries, injects boot scripts, runs QEMU, and extracts logs.

## Control Flow
Control flow is linear: prepare cache/temp image, mount partition, copy tests and `rc.local`, unmount, boot QEMU, then remount and copy logs out.

## State and Persistence Behavior
Persistent state is cached under `$HOME/.cache/go-fuse-freebsd`; temp state is created under that cache and loop devices must be cleaned by the operator if interrupted.

## Dependencies and Integration Points
Integrates with `posixtest`, `fs` tests, QEMU, KVM, UFS FUSE tooling, Go cross-compilation, and FreeBSD boot scripts.

## Risks and Edge Cases
Requires sudo, KVM, loop devices, a local UFS FUSE binary, network download, and careful cleanup. It appends loader config to the copied image only.

## Test Signals
Success signals are extracted `posixtest.log` and `fs.log`; failures often require inspecting QEMU serial output and mounted image contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/test-freebsd.bash -->
