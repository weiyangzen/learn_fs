# File Research: sources/os/bsd/openbsd-src/sbin/dmesg/Makefile

## Purpose
Builds the `dmesg` utility.

## Key Contents
- `PROG=dmesg`
- Installs `dmesg.8`.
- Links with `libkvm`.
- Adds `-Wall`.

## Notes
`libkvm` is required for `-M/-N` kernel memory/core reading support.
