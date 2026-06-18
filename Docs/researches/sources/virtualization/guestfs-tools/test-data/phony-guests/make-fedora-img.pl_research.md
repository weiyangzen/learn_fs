# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-fedora-img.pl

Perl generator for multiple Fedora-like test images.

Key behavior:
- Requires `LAYOUT` and `SRCDIR` environment variables.
- Uses `Sys::Guestfs` to create 1G raw images.
- Supports layouts:
  - `partitions`: MBR boot partition plus LVM root partition.
  - `partitions-md`: two disks with RAID1 md devices for boot and root, plus generated `mdadm.conf`.
  - `btrfs`: boot partition plus btrfs root with `root` and `home` subvolumes; creates empty output and exits if btrfs unavailable.
  - `lvm-on-luks`: LUKS container on second partition, then LVM root.
  - `luks-on-lvm`: LVM volumes, each formatted as separate LUKS devices.
- `init_lvm_root` creates VG/LVs, root ext2 with label/UUID, and extra empty ext2 filesystems for `virt-df` testing.
- Creates `/boot`, mounts boot device, and writes Fedora marker files: release files, fstab, hostname, RPM database and macros, journal archive, grub config, module config.
- Creates `/etc/shadow` with SELinux xattr.
- Uploads dynamic `/bin/ls`.
- Adds test files in `/etc` and `/bin`, symlink, FIFO, and device node.
- Installs `fedora-static-bin` as `/bin/sh`, `/bin/rpm`, and `/sbin/dracut`.
- Creates kernel/initrd/module paths matching `fedora.c`.
- Shuts down, closes guestfs, removes temporary fstab/mdadm, and renames `*-t` images to final names.

Research notes:
- This is the richest phony image generator in the group and supports storage stacks relevant to filesystem/block testing: LVM, MD RAID, btrfs subvolumes, and LUKS combinations.
