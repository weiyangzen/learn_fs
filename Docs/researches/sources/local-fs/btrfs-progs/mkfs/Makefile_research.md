# File Research: sources/local-fs/btrfs-progs/mkfs/Makefile

## Purpose
Small recursive make wrapper for mkfs-related build targets.

## Contents
- Includes `../Makefile.inc`.
- `all` invokes `$(MAKE) -C .. mkfs.btrfs`.
- `clean` removes local `*.o` and `*.o.d`.

## Risks
No complex logic. The directory relies on the parent makefile for actual build rules.
