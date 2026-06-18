# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-archlinux-img.sh

Shell generator for a minimal Arch Linux-like disk image.

Key behavior:
- Creates a 512M sparse MBR disk with one ext4 partition.
- Sets a stable ext filesystem UUID.
- Creates enough directories and files to satisfy inspection: `/etc/arch-release`, hostname, pacman local package metadata, `/bin/ls`, and grub config.
- Uploads `archlinux-package` fixture and dynamic x86_64 binary.
- Renames temporary image to `archlinux.img`.

Research notes:
- The image is designed for inspection heuristics, not actual boot.
