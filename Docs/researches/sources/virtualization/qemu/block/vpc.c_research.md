# File Research: sources/virtualization/qemu/block/vpc.c

QEMU block format driver for Connectix/Microsoft Virtual PC VHD images. It handles fixed and dynamic VHDs, including footer/header validation, dynamic BAT mapping, block allocation, and create paths.

Key responsibilities:
- Probe VHD images using the `conectix` footer/header signature.
- Parse VHD footers and dynamic disk headers, with big-endian field conversion and checksum validation.
- Determine visible disk size using Virtual PC CHS rules or footer `current_size`, with creator-app heuristics and runtime override via `force_size_calc`.
- Open fixed VHDs where data is directly addressed and dynamic VHDs with a Block Allocation Table.
- For dynamic images, maintain `pagetable`, `bat_offset`, `block_size`, `bitmap_size`, and `free_data_block_offset`.
- Map guest offsets to image offsets through `get_image_offset()`, including block bitmap updates for writes.
- Allocate new dynamic VHD blocks by writing bitmap, moving footer, and updating BAT.
- Create dynamic and fixed VHD images with valid footer, UUID, CHS geometry, dynamic header, and initial BAT.
- Register the `vpc` format `BlockDriver`.

Important structures:
- `VHDFooter`: 512-byte VHD hard disk footer, checked at compile time.
- `VHDDynDiskHeader`: 1024-byte dynamic disk header.
- `BDRVVPCState`: driver state for footer, BAT, block allocation metadata, runtime sizing overrides, and migration blocker.

Core flow:
- `vpc_open()` opens the file child, absorbs runtime options, reads the footer from the start or end depending on disk type, validates checksum, computes `bs->total_sectors`, and initializes dynamic BAT state when needed.
- `vpc_co_preadv()` returns direct reads for fixed disks. Dynamic reads return zeroes for unallocated blocks or read mapped image blocks.
- `vpc_co_pwritev()` writes directly for fixed disks. Dynamic writes allocate missing blocks and update block bitmaps/BAT/footer before writing data.
- `vpc_co_block_status()` reports fixed images as recursively mapped data and dynamic images as allocated data or zero regions.
- `vpc_co_create()` and `vpc_co_create_opts()` convert QAPI/legacy options, round sizes, calculate CHS-compatible geometry, and create fixed or dynamic images.

Notable constraints and risks:
- Maximum image size is capped at VHD’s 2040 GiB limit.
- Live migration is blocked for VPC/VHD images.
- The dynamic block bitmap is written as all-used for any block written, prioritizing correctness over sparse-read optimization.
- Geometry compatibility matters: without `force-size`, create rejects sizes not representable by the VHD CHS algorithm.
