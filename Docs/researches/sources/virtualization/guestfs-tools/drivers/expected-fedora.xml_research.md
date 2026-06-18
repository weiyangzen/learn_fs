# File Research: sources/virtualization/guestfs-tools/drivers/expected-fedora.xml

## Scope

Expected XML output fixture for `virt-drivers` on the phony Fedora guest.

## Contents

- Describes one BIOS firmware Linux operating system rooted at `/dev/VG/Root`.
- Includes Fedora release metadata, x86_64 arch, RPM/yum package metadata, and osinfo `fedora14`.
- Includes grub1 bootloader config path and one kernel entry.
- Kernel entry includes version, architecture, vmlinuz/initrd/modules paths, module `virtio_blk`, and `supports_virtio_blk`.

## Risks And Invariants

- Tests ignore the generated-by version comment.
- Any virt-drivers XML schema or phony Fedora kernel/module fixture change must update this expected file.
