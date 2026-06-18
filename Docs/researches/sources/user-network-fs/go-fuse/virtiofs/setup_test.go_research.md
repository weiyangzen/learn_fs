<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/setup_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/setup_test.go

## Purpose
Prepares host assets required by virtiofs QEMU tests and skips the package cleanly when unavailable.

## Important APIs, Types, and Functions
`TestMain`, `prepareAssets`, `ensureBusybox`, `findHostKernel`, `findVirtioFSModules`, and `moduleInsmodLines` are central.

## Control Flow
Setup finds the architecture-specific QEMU binary, creates a cache dir, downloads a static busybox if missing, locates the running kernel image, and asks `modprobe --show-depends virtiofs` for modules or builtin status.

## State and Persistence Behavior
Persistent cache lives in `$HOME/.cache/go-fuse-virtiofs`; discovered paths are stored in package-level `testAssets`.

## Dependencies and Integration Points
Depends on host QEMU, network access for busybox, `/boot` kernel naming, `modprobe`, and module compression handling in `ramdisk_test.go`.

## Risks and Edge Cases
It exits 0 to skip all tests on setup failure, which can hide missing coverage in CI. The busybox URL is x86-64-specific despite partial arm64 QEMU mapping.

## Test Signals
Test package startup is the signal; CI should log skip reasons and provide cached assets where deterministic coverage is required.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/setup_test.go -->
