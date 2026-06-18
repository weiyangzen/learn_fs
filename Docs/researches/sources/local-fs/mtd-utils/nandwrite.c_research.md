# File Research: sources/local-fs/mtd-utils/nandwrite.c

## Purpose
Writes page-aligned data, and optionally OOB data, to NAND MTD devices.

## Key Elements
Handles input file/stdin, input skip/size, start offset, bad-block skipping, no-ECC raw mode, auto/place OOB modes, OOB-only writes, padding, quiet mode, mark-bad-on-failure, and virtual eraseblock alignment. Buffers one aligned eraseblock of input so failed writes can be rewound and replayed after skipping or marking a bad block.

## Dependencies
Uses `libmtd`, `mtd/mtd-user.h`, POSIX file APIs, and `common.h`.

## Behavior/Risks
Raw NAND writer; incorrect options can corrupt devices. Start offset and input length must align unless padding is enabled. OOB and padding are mutually constrained. Partial final writes trigger failure if input remains unwritten.
