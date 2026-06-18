# File Research: sources/virtualization/guestfs-tools/inspector/expected-coreos.img.xml

Expected inspector output for a CoreOS test image.

Contents:
- Root: `/dev/sda5`
- OS: Linux distro `coreos`
- Product: `CoreOS 899.13.0`
- Major/minor: `899` / `13`
- Hostname: `coreos.invalid`
- Build ID: `2016-03-23-0120`
- osinfo: `coreos899.13`
- Mountpoints: `/` on `/dev/sda5`, `/usr` on `/dev/sda3`.
- Filesystems: ext4 `USR-A` and `ROOT` labels with fixed test UUIDs.
- Empty applications element.

Research relevance: regression oracle for CoreOS-specific inspection fields, labels, and split `/usr` layout.
