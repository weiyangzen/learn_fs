# File Research: sources/virtualization/guestfs-tools/make-fs/test-virt-make-fs.sh

## Role

Randomized functional test for `virt-make-fs`.

## Behavior

The script queries appliance feature availability with Perl `Sys::Guestfs` for ntfs3g, ntfsprogs, and btrfs. It builds random choices for filesystem type, image format, partition mode, extra size, label, and block size. Btrfs can be disabled with `SKIP_TEST_VIRT_MAKE_FS_BTRFS`; vfat is excluded because tar ownership restoration fails on FAT.

It creates a random zero-filled test file up to 8191 KiB, tars it, invokes `$VG virt-make-fs` with the random parameters, and removes the generated tar and output image.

## Research Notes

This is Monte Carlo-style coverage for combinations of filesystem type, partitioning, format, label, size, and sector size.
