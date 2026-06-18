# File Research: sources/virtualization/guestfs-tools/sparsify/test-virt-sparsify-in-place.sh

Runtime test for `virt-sparsify --in-place`.

Key behavior:
- Creates a 400M GPT boot/root-LVM image with ext4 filesystems through `guestfish -N`.
- Writes 300M to root and 10M to `/boot`, syncs, deletes both files, and unmounts.
- Records apparent disk usage before sparsification.
- Runs `virt-sparsify --debug-gc --in-place --format raw`.
- If exit status is 3, treats discard unsupported as skipped.
- Verifies the original image was large enough and that at least about 300000 KiB was recovered.
- Cleans image on success.

Research notes:
- This directly tests host sparse-file reclamation from deleted guest filesystem data.
