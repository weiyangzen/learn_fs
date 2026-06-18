# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-ubuntu-img.sh

Shell generator for a minimal Ubuntu-like disk image.

Key behavior:
- Creates temporary fstab and `lsb-release`.
- Builds a 512M MBR disk with `/boot` and root ext2 partitions.
- fstab includes a dummy encrypted swap mapping for regression coverage.
- Creates Ubuntu/Debian marker directories and files.
- Uploads dpkg status fixture and dynamic `/bin/ls`.
- Creates grub config.
- Removes temporary files and renames output to `ubuntu.img`.

Research notes:
- Covers Ubuntu inspection and encrypted swap fstab parsing scenario.
