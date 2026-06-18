# File Research: sources/virtualization/guestfs-tools/inspector/expected-archlinux.img.xml

Expected inspector output for an Arch Linux test image.

Contents:
- Root: `/dev/sda1`
- OS: Linux, Arch Linux, x86_64
- Major/minor versions are `0`.
- Package format/manager: `pacman`.
- Hostname: `archlinux.test`
- osinfo: `archlinux`
- Single ext4 root filesystem with fixed test UUID.
- One test package with epoch, version, release, arch, URL, and description.

Research relevance: regression oracle for Arch/pacman inspection behavior.
