# File Research: sources/virtualization/guestfs-tools/format/test-virt-format.sh

Functional test for `virt-format`.

Steps:
- Removes stale `test-virt-format.img`.
- Creates a guestfish `bootrootlv` test image.
- Runs `virt-format --filesystem=ext3 --format=raw -a test-virt-format.img`.
- Verifies `virt-filesystems` reports only `/dev/sda1`.
- Removes temporary image.

Research relevance: smoke-tests destructive reformatting and validates result through the inventory tool.
