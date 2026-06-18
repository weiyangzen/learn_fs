<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-image.sh -->
# sources/test-tools/syzkaller/tools/create-image.sh

## Purpose

Creates a Debian chroot and ext4 image for syzkaller guests.

## Important APIs, Types, and Functions

Flags arch/distribution/feature/output/perf/size; debootstrap, qemu-user-static, chroot apt, ssh-keygen, mkfs/mount/copy.

## Control Flow

Maps arch names, checks foreign emulation, debootstraps with optional archive fallback, runs second stage if needed, configures root SSH/DHCP/fstab/DNS/hostname, optional perf build, udev rule, and copies chroot to `<output>.img`.

## State and Persistence Behavior

Persists chroot dir, image, and generated SSH keypair; removes/recreates output dir.

## Dependencies and Integration Points

Requires sudo, debootstrap, apt repos, qemu/binfmt for foreign arch, kernel source if perf enabled.

## Risks and Edge Cases

`sudo rm -rf` on output demands validation; generated root key/passwordless login are testing-only; package drift can break builds.

## Test Signals

Build minimal/full host image, one foreign image, perf mode, then boot and SSH.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-image.sh -->
