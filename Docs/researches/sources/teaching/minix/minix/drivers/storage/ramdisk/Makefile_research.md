# File Research: sources/teaching/minix/minix/drivers/storage/ramdisk/Makefile

## Purpose

Builds the boot ramdisk image used by the MINIX memory driver and boot flow.

## Build Role

Defines a generated `image` target from proto files, service binaries, configuration files, generated `/dev` entries, and optional architecture-dependent components. Common programs include `fsck_mfs`, `loadramdisk`, `mfs`, `mount`, `procfs`, `minix-service`, shell, `sysenv`, and `umount`. i386 adds storage/input/bus services such as `floppy`, `pci`, `pckbd`, `at_wini`, optionally `ahci`, `virtio_blk`, `ext2`, and `acpi`. ARM adds `mmc`.

## Control Flow

The Makefile copies configuration files, creates password databases, generates device proto entries with `MAKEDEV.sh`, strips selected binaries, preprocesses the proto template with ramdisk feature defines, and invokes `TOOL_MKFSMFS` to create the MFS image. Recursive make rules are commented out to avoid parallel make issues.

## Dependencies

Depends on NetBSD/MINIX build variables, proto templates, host tools (`mkfsmfs`, `mtree`, `toproto`, `pwd_mkdb`, `sed`, `strip`), and prebuilt service binaries under the object tree.

## Risks

The ramdisk contents are conditional on architecture and build flags. Missing binaries are not built recursively by this file, so the surrounding build must provide them. Proto generation strips comments and blank lines through preprocessing; incorrect defines can materially change the boot image.
