# File Research: sources/os/linux/linux/fs/befs/io.h

## Purpose
Prototype header for low-level BeFS block read helper.

## Interface
- `befs_bread_iaddr()`: read a buffer for a BeFS inode/block-run address.

## Research Notes
Used by datastream code after logical-to-physical mapping.
