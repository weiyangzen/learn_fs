# File Research: sources/os/linux/linux/fs/befs/inode.h

## Purpose
Prototype header for BeFS inode validation.

## Interface
- `befs_check_inode()`: validates a raw on-disk inode against expected block number and flags.

## Research Notes
Small single-purpose header used by `linuxvfs.c`.
