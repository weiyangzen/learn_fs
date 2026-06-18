# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-debian-img.sh

Shell generator for a minimal Debian-like disk image.

Key behavior:
- Creates temporary `debian.fstab`.
- Builds a 512M MBR disk with `/boot` partition and LVM PV.
- Creates LVs for root, usr, var, and home.
- Formats ext2 filesystems with stable UUIDs and label `BOOT`.
- Mounts full layout, creates Debian directories and marker files.
- Uploads fstab, Debian version, hostname, dpkg status fixture, dynamic `/bin/ls`, syslog fixture, and grub config.
- Removes temporary fstab and renames output to `debian.img`.

Research notes:
- Exercises inspection of Debian with LVM-backed multi-filesystem layout.
