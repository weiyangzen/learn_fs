# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/gcd_hupper.c

## Purpose
Sends `SIGHUP` repeatedly to the JFFS2 garbage-collector daemon for the tested MTD device.

## Key Elements
Scans `/proc/*/stat` for process names beginning `(jffs2_gcd_mtd`, derives the mounted MTD index from mount table device names, finds the matching GC PID, then sends `SIGHUP` with optional repeat and sleep.

## Dependencies
Uses `/proc`, mount table parsing, signals, and shared `tests.h`.

## Behavior/Risks
Requires permissions to signal kernel/helper task. Process-name and MTD-index parsing are JFFS2-specific and fragile outside legacy MTD naming.
