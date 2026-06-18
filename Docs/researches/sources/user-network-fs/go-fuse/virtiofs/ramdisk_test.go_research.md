<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/ramdisk_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/ramdisk_test.go

## Purpose
Builds gzipped cpio initrds for virtiofs QEMU tests, including busybox links, decompressed kernel modules, init scripts, and extra files.

## Important APIs, Types, and Functions
Key helpers are `decompressModule`, `stripCompression`, and `mkinitRam`.

## Control Flow
`mkinitRam` creates a temp root, copies busybox, creates standard directories, embeds modules and extra files, creates many busybox symlinks, writes or links init, then runs `cpio --null -ov --format=newc` through gzip to the output path.

## State and Persistence Behavior
State is temporary filesystem content and the final initrd file; it does not remove the temp build dir explicitly.

## Dependencies and Integration Points
Depends on external `xz`, `zstd`, `cpio`, gzip, busybox, and module paths discovered by setup code.

## Risks and Edge Cases
Missing tools or compressed modules fail at runtime. Not cleaning the temp directory can leave artifacts. The hardcoded busybox command list may include commands not supported by the chosen binary.

## Test Signals
Virtiofs tests validate initrd bootability; focused tests could inspect cpio contents and module decompression paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/ramdisk_test.go -->
