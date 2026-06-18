# File Research: sources/virtualization/guestfs-tools/inspector/example-fedora.xml

Example `virt-inspector` XML for Fedora 18 x86_64.

Contents:
- Root: `/dev/fedora/root`
- OS: Linux, Fedora, product `Fedora release 18 (Spherical Cow)`
- Package format/manager: `rpm` / `yum`
- Mountpoints: `/` and `/boot`.
- Filesystems: ext4 root, swap, ext4 boot with UUIDs.
- Applications section is shortened but shows RPM package metadata.
- Includes a base64 PNG icon.

Research relevance: documentation fixture for RPM/yum Linux inspection output.
