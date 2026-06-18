# File Research: sources/virtualization/guestfs-tools/inspector/example-debian.xml

Example `virt-inspector` XML for a Debian 5 x86_64 guest.

Contents:
- Root: `/dev/debian5x64.home.annexia.org/root`
- OS: Linux, Debian, product `5.0.6`
- Package format/manager: `deb` / `apt`
- Hostname included.
- Mountpoints include `/`, `/tmp`, `/usr`, `/var`, `/boot`, `/home`.
- Filesystems include ext3 LVs, swap LV, and ext2 `/dev/sda1`, with UUIDs.
- Applications section is shortened but demonstrates package entries.
- Includes a base64 PNG icon.

Research relevance: documentation fixture showing expected inspector schema for Debian with LVM-heavy layout.
