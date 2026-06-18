# File Research: sources/virtualization/guestfs-tools/inspector/expected-debian.img.xml

Expected inspector output for a Debian test image.

Contents:
- Root: `/dev/debian/root`
- OS: Linux, Debian, x86_64
- Product: `5.0.1`
- Package format/manager: `deb` / `apt`
- Hostname: `debian.invalid`
- osinfo: `debian5`
- Mountpoints include `/`, `/usr`, `/var`, `/boot`, `/home`.
- Filesystems are ext2 LVs plus `/dev/sda1` labeled `BOOT`, with fixed test UUIDs.
- Applications include three test packages with version, release, arch, URL, source package, summary, and multiline description.

Research relevance: regression oracle for Debian inspection, LVM mountpoint mapping, labels, package metadata, and multiline description serialization.
