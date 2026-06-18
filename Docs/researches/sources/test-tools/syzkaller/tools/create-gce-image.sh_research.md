<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-gce-image.sh -->
# sources/test-tools/syzkaller/tools/create-gce-image.sh

## Purpose

Creates a minimal bootable Linux raw disk for syzkaller/GCE from userspace and kernel image.

## Important APIs, Types, and Functions

Args userspace/kernel/arch; loop or nbd, fdisk, mkfs.ext4, mount/copy, SSH/network/fstab/udev injection, grub-install or zipl.

## Control Flow

Validates inputs, creates disk.raw, partitions per arch, formats/mounts, copies userspace/kernel, configures serial/DHCP/debugfs/securityfs/configfs/binder/i915/vim2m/passwordless SSH, optional sysctl/cmdline, installs bootloader.

## State and Persistence Behavior

Writes disk.raw and temporary disk.mnt/device attachments; trap cleans loop/nbd/mounts.

## Dependencies and Integration Points

Requires sudo, block device tooling, grub/zipl, init-capable userspace, and kernel image naming by arch.

## Risks and Edge Cases

Destructive to local disk.raw/disk.mnt; Debian path assumptions; failures may leave mounts/devices.

## Test Signals

Boot amd64 and one non-x86 image in QEMU; verify serial, DHCP, SSH, mounts, cmdline/sysctl.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-gce-image.sh -->
