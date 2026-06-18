# File Research: sources/os/bsd/openbsd-src/sbin/quotacheck/Makefile

## Purpose

Builds `quotacheck`.

## Build Definition

The program is `quotacheck`, with sources `quotacheck.c`, `preen.c`, and `fsutil.c`. It includes `../fsck`, uses `.PATH` to reuse fsck helper sources, installs `quotacheck.8`, and links against `libutil`.

## Coupling

This utility shares preen/check infrastructure with `fsck` through `preen.c` and `fsutil.c`.
