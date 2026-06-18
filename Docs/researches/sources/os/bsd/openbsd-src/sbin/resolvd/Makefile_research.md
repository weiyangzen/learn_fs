# File Research: sources/os/bsd/openbsd-src/sbin/resolvd/Makefile

## Purpose

Builds `resolvd`.

## Build Definition

The program is `resolvd`, with source `resolvd.c` and manual page `resolvd.8`. It enables strict warnings and includes the current directory. `LDSTATIC=` is cleared so the daemon is not built static by default.

## Notable Detail

A commented `DEBUG` assignment documents a local debug build configuration.
