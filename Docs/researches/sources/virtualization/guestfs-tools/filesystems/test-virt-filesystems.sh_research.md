# File Research: sources/virtualization/guestfs-tools/filesystems/test-virt-filesystems.sh

Functional test for `virt-filesystems` against the Fedora phony guest image.

Checks:
- Default output lists mountable filesystems only, sorted:
  `/dev/VG/LV1`, `/dev/VG/LV2`, `/dev/VG/LV3`, `/dev/VG/Root`, `/dev/sda1`.
- `--all --long --uuid -h --no-title` includes unique names for VG, LVs, block device, and partitions.
- Runs through `$VG`, allowing valgrind wrapping.

Research relevance: confirms default filtering and `--all --long` object coverage.
