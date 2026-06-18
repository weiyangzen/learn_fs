# File Research: sources/os/linux/linux-stable/fs/overlayfs/Makefile

## Scope

This Makefile wires the overlayfs module/object build into the kernel build system.

## Build Rules

- `obj-$(CONFIG_OVERLAY_FS) += overlay.o` builds overlayfs when the Kconfig option is enabled.
- `overlay-objs` combines the implementation objects:
  - `super.o`
  - `namei.o`
  - `util.o`
  - `inode.o`
  - `file.o`
  - `dir.o`
  - `readdir.o`
  - `copy_up.o`
  - `export.o`
  - `params.o`
  - `xattrs.o`

## Dependencies And Role

- This file defines the compilation unit boundaries for the overlayfs subsystem.
- The listed objects provide mount/lookup/utilities/inode/file/directory/readdir/copy-up/export/parameter/xattr functionality for the final `overlay.o`.

## Risks And Invariants

- Any new overlayfs source file must be added to `overlay-objs` or it will not link into the module/built-in filesystem.
