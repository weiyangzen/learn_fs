# File Research: sources/virtualization/guestfs-tools/inspector/example-rhel-6.xml

Example `virt-inspector` XML for RHEL 6.3 i386.

Contents:
- Root: `/dev/vg_rhel6x32/lv_root`
- OS: Linux, RHEL, product `Red Hat Enterprise Linux Server release 6.3 (Santiago)`
- Package format/manager: `rpm` / `yum`
- Hostname included.
- Mountpoints: `/` and `/boot`.
- Filesystems: ext4 root LV, swap LV, ext4 boot partition.
- Applications section is shortened but shows RPM metadata.
- Includes a very large base64 PNG icon.

Research relevance: documentation fixture for RHEL inspection, LVM root layout, and large icon output.
