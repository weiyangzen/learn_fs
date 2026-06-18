# File Research: sources/local-fs/e2fsprogs/misc/badblocks.c

## Purpose
Implements the `badblocks` scanner for finding bad sectors/blocks on a device.

## Main Modes
- `test_ro()`: read-only scan, optionally comparing against a supplied pattern.
- `test_rw()`: destructive write-mode scan using default or user-specified patterns, then reads back and compares.
- `test_nd()`: non-destructive read-write scan that saves original data, writes test data, verifies it, then restores saved data, including signal cleanup restoration.

## Support Logic
- Maintains an in-memory ext2 badblocks list and emits new bad blocks through `bb_output()`.
- Skips known-bad blocks loaded from `-i`.
- Supports progress reporting via alarm-driven status updates.
- Uses aligned buffers and toggles `O_DIRECT` when buffer, size, and offset alignment permit unless `-B` requests buffered I/O.
- `check_mount()` refuses unsafe write tests on mounted or busy devices unless forced/internal bypass options allow it.

## CLI Contract
Parses block size, blocks-at-once, delay factor, max bad blocks, input/output files, clean-pass repetition, test patterns, verbose/progress flags, destructive/non-destructive mode, force, buffered I/O, and internal exclusive-check bypass.

## Integration
Uses libext2fs helpers for device sizing, mount checks, syncing, badblocks list creation, and large seeks. Its output format is consumed by `e2fsck` and `mke2fs`.

## Risks / Notes
- Classic badblocks format is limited to 32-bit block numbers.
- Signal handling in non-destructive mode is important because it restores saved blocks before exiting.
- Incorrect block size makes output unusable for filesystem-level bad block marking.
