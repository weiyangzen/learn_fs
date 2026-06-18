# File Research: sources/local-fs/udftools/mkudffs/main.c

Main program and output writer for `mkudffs`.

Device/image probing:
- `valid_offset` checks whether a byte offset can be read.
- `get_blocks` determines block count from explicit options, block ioctls, floppy ioctls, regular file size, or binary search over readable offsets.
- `detect_blocksize` uses `BLKSSZGET` to choose a suitable logical block size when not specified.
- `is_whole_disk` inspects sysfs to distinguish whole block devices from partitions or stacked devices.
- `is_removable_disk` reads sysfs `removable`.

Writing:
- `write_func` iterates planned extents and descriptors.
- It seeks to descriptor block offsets, concatenates descriptor data payloads, block-aligns them, writes unless `FLAG_NO_WRITE` is set, and optionally zeroes reserved/unallocated boot-area ranges unless boot-area preservation is requested.

Main flow:
- Ensures standard fds exist.
- Sets locale.
- Initializes `struct udf_disc`.
- Parses command-line options.
- Opens the target device/image with `O_EXCL`.
- Determines block size and block count.
- Selects default boot-area behavior: preserve, MBR, or erase.
- Prints target metadata: filename, label, UUID, block size, block count, UDF revision, and optional start block.
- Calls generation helpers: `split_space`, `setup_mbr`, `setup_vrs`, `setup_anchor`, `setup_partition`, and `setup_vds`.
- Prints VAT block if present and dumps space layout.
- Emits warnings for tiny filesystems, weak Volume Set Identifier UUID data, and partition-target Apple compatibility.
- Creates a new image file when the target does not exist and block count was specified.
- Writes the built UDF structures, fsyncs, and closes.

Key role: ties CLI options, device geometry, filesystem layout generation, and final output I/O into the `mkudffs` executable.
