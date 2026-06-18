# File Research: sources/os/linux/linux/fs/overlayfs/Makefile

## Role

Build definition for the OverlayFS kernel object.

## Main Contents

`obj-$(CONFIG_OVERLAY_FS) += overlay.o` builds the filesystem when enabled. `overlay-objs` links these implementation units:

`super.o`, `namei.o`, `util.o`, `inode.o`, `file.o`, `dir.o`, `readdir.o`, `copy_up.o`, `export.o`, `params.o`, and `xattrs.o`.

## Research Notes

The files in this group cover major object members of the combined `overlay.o`: namespace mutation, copy-up, export, file operations, and inode operations.
