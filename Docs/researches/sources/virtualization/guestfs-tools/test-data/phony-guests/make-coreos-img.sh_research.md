# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-coreos-img.sh

Shell generator for a minimal CoreOS-like disk image.

Key behavior:
- Writes a temporary CoreOS-style `os-release` file.
- Creates a 512M GPT disk with EFI, BIOS-BOOT, USR-A, USR-B, and ROOT partitions.
- Formats FAT and ext4 partitions, labels/UUIDs USR-A and ROOT.
- Mounts ROOT and USR-A, creates CoreOS-like `/usr` layout and symlinks.
- Writes update config, hostname, and installs `os-release`.
- Removes temporary release file and renames output to `coreos.img`.

Research notes:
- Uses partition names and `/usr` layout to exercise CoreOS inspection paths.
