# File Research: sources/local-fs/e2fsprogs/misc/e2image.8.in

## Purpose
Manual page template for `e2image`, which saves critical ext2/ext3/ext4 metadata to image files and can restore classic metadata images.

## Documented Interface
- Standard metadata image:
  - `e2image [options] device image-file`
- Install/restore:
  - `e2image -I device image-file`
- Raw/QCOW2:
  - `e2image [-r|-Q] [-a] [-f] [-b superblock] [-B blocksize] [-c] [-n] [-p] [-s] [-o src_offset] [-O dest_offset] device image-file`

## Major Options
- `-a`: include all file data for raw/QCOW2.
- `-b`, `-B`: alternate superblock/block size.
- `-c`: compare target blocks and skip identical writes in raw mode.
- `-f`: allow imaging read-write mounted filesystems.
- `-I`: install metadata image back to a device.
- `-n`: no writes; print blocks that would be written.
- `-o`, `-O`: source/destination offsets.
- `-p`: progress.
- `-Q`: QCOW2 image.
- `-r`: raw sparse image.
- `-s`: scramble directory entries.

## Important Notes
- Raw images preserve metadata at original filesystem-relative offsets and are sparse.
- QCOW2 images are compact but not sparse and can be processed by QCOW2-aware tools.
- `-I` is documented as a desperation recovery measure because stale metadata restore can lose data.
- Output to stdout is only supported for raw image creation.
