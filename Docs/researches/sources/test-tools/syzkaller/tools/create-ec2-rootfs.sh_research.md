<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-ec2-rootfs.sh -->
# sources/test-tools/syzkaller/tools/create-ec2-rootfs.sh

## Purpose

Creates or resizes an Amazon Linux 2023 EC2/QEMU root filesystem image.

## Important APIs, Types, and Functions

Parses format/name/platform/size; uses truncate, mkfs, loop mount, Docker export, tar, chroot, dnf, systemctl, resize2fs/xfs_growfs.

## Control Flow

Existing image path resizes and exits; new path formats image, exports AL2023 container, installs systemd/network/SSH tools, enables DHCP, configures passwordless root SSH, and unmounts.

## State and Persistence Behavior

Persists the rootfs image; temporary mount dir/container/image cache are side effects.

## Dependencies and Integration Points

Requires sudo, Docker, loop devices, mkfs/resizer tools, DNF/network access, and compatible platform emulation.

## Risks and Edge Cases

Assumes `/dev/loop0` during resize; failures can leave mounts; passwordless root is unsafe outside fuzzing guests.

## Test Signals

Create/resize ext4 and xfs images, boot with documented QEMU, verify DHCP and SSH.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-ec2-rootfs.sh -->
