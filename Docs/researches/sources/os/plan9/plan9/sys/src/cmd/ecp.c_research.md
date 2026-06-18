# File Research: sources/os/plan9/plan9/sys/src/cmd/ecp.c

Error-tolerant sector copy utility.

Key behavior:
- Copies a specified number of sectors from source to destination using large block transfers.
- On I/O failure, falls back to single-sector retries and reports bad-sector ranges.
- Supports confirmation, progress output, reverse copy order, input reblocking, maximum consecutive error limits, sector-size/block-size options, source/destination starting sectors, optional byte “swizzle”, and separate verification pass.
- Treats short reads as I/O errors but can reblock pipe input.
- Uses magic sentinels to detect reads that falsely report success without changing the buffer.
- Verifies by rereading source and destination after copy to avoid controller cache effects.

Filesystem relevance:
- Block-device/file image copy tool for damaged media and low-level filesystem/device recovery workflows.
