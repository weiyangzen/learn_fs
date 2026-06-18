# File Research: sources/virtualization/guestfs-tools/sparsify/test-virt-sparsify.sh

Runtime test for copy-mode `virt-sparsify`.

Key behavior:
- Creates a raw test image with boot/root LVM layout.
- Writes and deletes 300M root data and 10M boot data.
- Runs `virt-sparsify --debug-gc --format raw input --convert qcow2 output`.
- Verifies source disk usage is at least 310000 KiB and qcow2 output is no larger than 15000 KiB.
- Removes both images on success.

Research notes:
- Tests both sparsification and output conversion to qcow2.
