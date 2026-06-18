# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.c

Main program for `debugreiserfs`.

Core responsibilities:
- Parses documented and hidden command-line options.
- Opens the ReiserFS filesystem and journal.
- Dispatches to dump, pack, unpack, corruption, scan, recover, stat, bad-block extraction, and zeroing modes.
- Initializes scan bitmaps from on-disk bitmap, full device, unused blocks, or an external bitmap file.

Important modes:
- `DO_DUMP`: print superblock, filesystem state, optional journal/objectid/bitmap/tree details.
- `DO_PACK`: call `pack_partition` or `pack_one_block`.
- `DO_UNPACK`: call `do_unpack` before opening a filesystem.
- `DO_SCAN`, `DO_SCAN_FOR_NAME`, `DO_LOOK_FOR_NAME`, `DO_SCAN_JOURNAL`: initialize bitmap then call `do_scan`.
- `DO_CORRUPT_ONE`, `DO_CORRUPT_FILE`, `DO_RANDOM_CORRUPTION`: reopen read-write and corrupt.
- `DO_EXTRACT_BADBLOCKS`: walk internal bad-block list and write block numbers.
- `DO_ZERO`: zero all blocks selected by the scan bitmap.

Key helpers:
- `print_disk_tree`: recursive internal-tree printer and block statistics collector.
- `print_disk_blocks`: scans selected bitmap blocks and prints recognizable ReiserFS metadata.
- `print_one_block`: reports bitmap use state and prints or packs one block.
- `init_bitmap`: shared scan-area setup.

Notable risks/quirks:
- Hidden/undocumented options expose experimental scan/map/recover behavior.
- `do_corrupt_blocks` prints debug messages around `free(line)`.
- `debugreiserfs_zero_reiserfs` destructively zeroes selected blocks.
