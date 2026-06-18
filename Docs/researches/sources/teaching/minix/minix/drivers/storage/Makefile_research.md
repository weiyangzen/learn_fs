# File Research: sources/teaching/minix/minix/drivers/storage/Makefile

## Purpose
Top-level storage-driver subdirectory makefile for MINIX. It selects which storage driver subdirectories are built for the target architecture and image mode.

## Key Behavior
- Includes `<bsd.own.mk>` for build variables.
- When `MKIMAGEONLY == "no"`, adds runtime storage drivers:
  - On `i386`: `ahci`, `fbd`, `filter`, `virtio_blk`.
  - On `earm`: `mmc`.
  - Always: `vnd`.
- On `i386`, always adds legacy `at_wini` and `floppy`, even outside the `MKIMAGEONLY == "no"` block.
- Enforces build order for ramdisk-related targets:
  - `ramdisk` and `memory` are separated with `.WAIT`.
  - Comment notes `memory` must be last because the ramdisk image depends on executables from earlier targets.
- Includes `<bsd.subdir.mk>` to recurse into `SUBDIR`.

## Integration Notes
This is build orchestration only; it does not define binaries itself. Its main coupling is to architecture variables and to storage subdirectories that each include `minix.service.mk`.

## Risks
Changing order around `ramdisk`/`memory` can break image construction. Architecture conditionals determine which block drivers exist in a build image.
