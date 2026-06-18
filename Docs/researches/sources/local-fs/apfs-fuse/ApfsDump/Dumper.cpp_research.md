# File Research: sources/local-fs/apfs-fuse/ApfsDump/Dumper.cpp

`Dumper` implements physical APFS container dumping. `Initialize()` detects GPT APFS partition offsets for the main and optional tier2 device, reads the NX superblock, adopts the APFS block size, and verifies the superblock checksum.

`DumpContainer()` reads and dumps the NX superblock, checkpoint map, spaceman, CAB/CIB metadata, bitmap blocks, and allocated blocks. It uses spaceman allocation bitmaps to decide which physical blocks to feed into `BlockDumper`, including Fusion tier2 address translation via `FUSION_TIER2_DEVICE_BYTE_ADDR`.

`DumpBlockList()` scans the main device, and optionally tier2, printing a compact table of APFS object headers and B-tree node metadata when checksums validate, or `Data` for non-APFS/non-verified blocks.

`Read()` maps APFS physical block addresses to byte offsets in main or tier2 devices. `Decrypt()` contains a manual AES-XTS path, but encryption is gated behind disabled code that requires hardcoded VEK material.

Notable risks: some code assumes 4 KiB blocks in `DumpBlockList()` despite dynamic block size elsewhere. The tier2 block-list branch appears suspicious because it calls `Read(block + off, bid, 1)` where `off` is a huge APFS address-derived block offset, not a buffer offset.
