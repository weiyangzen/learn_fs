<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-buildroot-image.sh -->
# sources/test-tools/syzkaller/tools/create-buildroot-image.sh

## Purpose

Buildroot automation for syzkaller Linux guest images across several architectures.

## Important APIs, Types, and Functions

Env vars `TARGETARCH`, `NOMAKE`, `LINUX_VERSION`, `LINUX_KERNEL_CONFIG`; Buildroot defconfigs; generated rootfs/post-image scripts; `make olddefconfig`/`make`.

## Control Flow

Pins Buildroot checkout, appends common/per-arch config, patches package defaults, writes rootfs hooks for debugfs/securityfs/configfs/SSH/host keys/bootloader, adjusts arm64 image config, and optionally builds.

## State and Persistence Behavior

Mutates the Buildroot checkout and output tree: `.config`, package files, scripts, custom genimage config, and images.

## Dependencies and Integration Points

Requires external Buildroot checkout, host build deps, network/package access, and kernel config path; used for syzkaller VM image production.

## Risks and Edge Cases

Invasive if run in wrong directory; version-pinned sed/hash patches can drift; passwordless root SSH is testing-only.

## Test Signals

Run with `NOMAKE=yes` per arch, then boot representative images and verify SSH/KCOV/filesystem mounts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-buildroot-image.sh -->
