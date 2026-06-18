# File Research: sources/os/linux/linux-stable/fs/efs/Makefile

## Summary
Builds the EFS filesystem module.

## Main Contents
`efs.o` is built from:
- `super.o`
- `inode.o`
- `namei.o`
- `dir.o`
- `file.o`
- `symlink.o`

## Risks
The module is small and all behavior is read-only block, inode, directory, lookup, and symlink support.
