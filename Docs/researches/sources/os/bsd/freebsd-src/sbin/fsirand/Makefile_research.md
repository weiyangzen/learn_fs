# File Research: sources/os/bsd/freebsd-src/sbin/fsirand/Makefile

## Purpose

Builds the `fsirand` UFS generation-number randomizer.

## Build Definition

- Program: `fsirand`
- Manual: `fsirand.8`
- Package: `ufs`
- Links `libufs`
- Warning level set to 3

## Integration Notes

The source is standalone except for UFS/FFS/libufs APIs.
