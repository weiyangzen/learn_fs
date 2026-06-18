# File Research: sources/teaching/minix/minix/fs/ext2/Makefile

## Purpose

Builds the MINIX ext2 filesystem service.

## Build Role

Defines `PROG=ext2` with ext2 service sources for block allocation, links, mount, misc, open/protect/read/write, stats, utilities, inode allocation/inode handling, main, path, and superblock logic. Links against `libminixfs`, `libfsdriver`, `libbdev`, and `libsys`, sets `WARNS=3`, and includes `minix.service.mk`.

## Dependencies

Depends on MINIX filesystem service libraries and block-device access library.

## Risks

This Makefile defines the compilation surface for the ext2 service. Missing a source from `SRCS` would remove filesystem behavior at link time; library order also matters because the service uses shared fsdriver/minixfs/bdev support.
