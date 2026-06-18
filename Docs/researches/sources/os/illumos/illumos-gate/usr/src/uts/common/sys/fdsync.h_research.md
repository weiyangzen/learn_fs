# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdsync.h

## Purpose

`fdsync.h` is a private header for the internal `fdsync` system call. The comments state that it should not be shipped and that `fdsync` is not a public libc interface.

## Main Types

`fdsync_mode_t` selects the sync operation to perform on a file descriptor.

Values are:

`FDSYNC_FS`: sync the filesystem containing the file descriptor, corresponding to `syncfs(3C)`.

`FDSYNC_FILE`: sync outstanding file data and metadata, corresponding to `fsync(3C)`.

`FDSYNC_DATA`: sync outstanding file data only, corresponding to `fdatasync(3C)`.

## Research Notes

This file is small but directly filesystem-relevant. It defines the kernel-private dispatch mode for fd-based syncing and separates whole-filesystem sync from file and data-only sync behavior.
