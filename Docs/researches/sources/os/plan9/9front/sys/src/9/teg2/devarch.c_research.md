# File Research: sources/os/plan9/9front/sys/src/9/teg2/devarch.c

Implements Plan 9 architecture device `#P` for Tegra/ARM. It supports dynamically adding read/write files via `addarchfile`, backed by `Dirtab` entries and function tables.

The default exported files are `cputype`, which reports ARM CPU name and MHz, and `timebase`, which reports `cycles()` as a fixed-width hex value. An `nsec` file exists but is commented out.

The device follows normal Plan 9 devtab operations: attach, walk, stat, open, read directory or handler, and write handler dispatch.
