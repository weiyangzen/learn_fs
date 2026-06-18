# File Research: sources/local-fs/mtd-utils/nanddump.c

## Purpose
Dumps raw NAND page data, optionally including OOB data and ECC-status diagnostics.

## Key Elements
Supports output file/stdout, start/length, pretty/canonical hex dumps, raw no-ECC mode, OOB inclusion/omission, quiet mode, and bad-block policies `skipbad`, `padbad`, and `dumpbad`. Uses libmtd for geometry, bad-block checks, page reads, and OOB reads.

## Dependencies
Depends on `mtd/mtd-user.h`, `libmtd.h`, POSIX I/O, and `common.h`.

## Behavior/Risks
Refuses binary output to a tty unless forced. Requires page-aligned start offsets. Bad-block handling changes output semantics substantially: `skipbad` extends the read window to preserve good-data length, while `padbad` emits `0xff` data for bad blocks.
