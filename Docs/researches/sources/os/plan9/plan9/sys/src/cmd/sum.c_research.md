# File Research: sources/os/plan9/plan9/sys/src/cmd/sum.c

This file implements checksum calculation in three historical formats.

Key behavior:
- Default mode computes a 32-bit CRC with length folded into the final CRC.
- `-r` computes the Research Unix rotating 16-bit checksum with 1024-byte block count.
- `-5` computes the System V-style additive checksum with 512-byte block count.
- Reads stdin or named files and prints checksum, block/size count, and optional filename.

Important details:
- The checksum function is called with `buf == nil` as a finalization/printing step.
- The CRC table is embedded.
- Read/open errors are reported per file and returned via exit status string.

Filesystem relevance:
- Indirect: file integrity utility over arbitrary file contents.
