# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiorom.c

## Role

`gsiorom.c` defines a `%rom%` IODevice intended for an embedded compressed in-memory filesystem image, but this implementation is only a stub.

This is Ghostscript virtual filesystem adapter scaffolding, not a real filesystem implementation in this copy.

## Main Interfaces

- Device definition: `gs_iodev_rom`.
- Device operations: `iodev_rom_init`, `iodev_rom_open_file`.
- State type: `romfs_state` with an `image` pointer.

## Core Behavior

- Initialization allocates a `romfs_state` and sets `image` to `NULL`, but does not assign it to `iodev->state` in the code shown.
- Opening any file ignores `fname`, `namelen`, and `access`, allocates a buffer containing the fixed string `this came from the compressed romfs.`, and returns it as a read-string stream.

## Notable Risks

The file advertises compressed ROM filesystem access, but the implementation is fake. It leaks/loses the allocated `romfs_state` because it is not stored on the IODevice, and `iodev_rom_open_file` does not check allocation failure for `s_alloc`.
