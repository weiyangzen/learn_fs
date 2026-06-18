# File Research: sources/local-fs/e2fsprogs/misc/e2image.c

## Purpose
Implements `e2image`, which creates classic ext2 image files, raw sparse metadata/data images, QCOW2 images, QCOW2-to-raw conversion, and classic metadata image installation.

## Main Image Modes
- Classic metadata image:
  - Writes an `ext2_image_hdr`, superblock, inode tables, block bitmap, and inode bitmap using ext2fs image helpers.
- Raw image:
  - Writes selected filesystem blocks at their filesystem-relative offsets, usually sparse.
  - Includes metadata, directory blocks, indirect/extent metadata, journal/quota/orphan-file blocks, and optionally all data blocks.
- QCOW2 image:
  - Writes metadata/data blocks into a generated QCOW2 structure with L1/L2/refcount metadata.
- Install mode:
  - Restores inode table metadata from a classic image to a target device.
- QCOW2 input conversion:
  - Detects QCOW2 input when raw output is requested and converts it with `qcow2_write_raw_image`.

## Important Functions
- `align_offset`, `get_bits_from_size`: block/cluster alignment helpers.
- `generic_write`: central write/no-op write helper.
- `write_header`: writes zero-padded headers at file start.
- `write_image_file`: classic image writer.
- `use_inode_shortcuts`, `meta_get_blocks`, `meta_check_directory`, `meta_read_inode`: short-circuit ext2fs callbacks during inode scanning.
- `mark_table_blocks`: marks superblock, descriptors, MMP, inode tables, block bitmaps, and inode bitmaps as metadata.
- `scramble_dir_block`: anonymizes directory entry names and zeros unused directory entry slack.
- `output_meta_data_blocks`: raw sparse output loop with optional progress, zero-block skipping, compare-before-write, and in-place move handling.
- `initialize_qcow2_image`, `init_l1_table`, `init_l2_cache`, `init_refcount`: QCOW2 setup.
- `add_l2_item`, `update_refcount`, `sync_refcount`, `flush_l2_cache`: QCOW2 metadata maintenance.
- `output_qcow2_meta_data_blocks`: QCOW2 data and metadata writer.
- `write_raw_image_file`: scans inodes, builds block maps, and dispatches raw/QCOW2 output.
- `install_image`: restores a classic image to a device.
- `check_qcow2_image`: identifies QCOW2 input.
- `main`: option validation, mount safety checks, open paths, and mode dispatch.

## Dependencies
- ext2fs core, private ext2fs structures, e2image helpers, QCOW2 helpers.
- quota inode helpers.
- `support/plausible.h`.
- POSIX large-file I/O, signals, and filesystem stat APIs.

## Notes and Edge Cases
- `-a` and `-b` are only valid with raw or QCOW2 images.
- Offsets and in-place move mode are raw-only; move mode also requires all-data mode.
- Raw imaging normally refuses read-write mounted filesystems unless `-f` is supplied.
- Directory scrambling preserves `.` and `..`, replaces other names with deterministic `A...` variants, and repairs malformed directory record lengths enough to continue.
- In-place rightward moves copy in reverse chunks to avoid overwriting source data before it is copied.
- `-c` compare-before-write is raw-only and not supported with stdout.
- `-p` progress is raw-only.
