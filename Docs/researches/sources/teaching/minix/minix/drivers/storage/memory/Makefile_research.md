# File Research: sources/teaching/minix/minix/drivers/storage/memory/Makefile

## Purpose

Builds the MINIX memory driver and embeds the boot image ramdisk object.

## Build Role

Defines `PROG=memory` with `memory.c` and generated `imgrd.mfs` as sources. Converts the ramdisk image into an object with `objcopy -Ibinary`, disables bitcode, links against `libblockdriver` and `libchardriver`, and includes `minix.service.mk`.

## Control Flow

If `../ramdisk/image` does not exist, `touch-genfiles` creates a deterministic empty placeholder. `imgrd.mfs` symlinks to the ramdisk image. The commented-out recursive make rules indicate this tree avoids invoking parallel sub-makes.

## Dependencies

Depends on the ramdisk image path, host linker/objcopy support for binary objects, and generated symbols consumed by `local.h`.

## Risks

If the ramdisk image is missing, the build can proceed with a placeholder, which is useful for dependency generation but can hide an empty boot image if not regenerated in the intended build flow.
