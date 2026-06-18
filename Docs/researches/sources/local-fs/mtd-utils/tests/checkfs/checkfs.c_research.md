# File Research: sources/local-fs/mtd-utils/tests/checkfs/checkfs.c

## Purpose
Power-fail filesystem consistency test harness.

## Key Elements
On startup, checks `file0..file99` CRC-tagged files, logs failures to `logfile`, repairs bad files up to a configurable error limit, updates `cycleCnt`, sends an “OK to power me down” message over a serial port, then loops forever rewriting randomly sized CRC-protected files using single whole-buffer writes and truncation.

## Dependencies
Uses `common.h` for `MAX_NUM_FILES` and boolean constants, `comm.c`’s `do_pwr_dn`, POSIX file APIs, termios serial setup, `fdatasync`, `sync`, and an embedded CRC-CCITT table.

## Behavior/Risks
Designed for destructive power-cycle testing in the current working directory. It assumes `makefiles` has already created `file*` and `cycleCnt`. Serial defaults to `/dev/ttyS0` at 9600 7E1. File naming comments mention padded names, but implementation uses `file%i`.
