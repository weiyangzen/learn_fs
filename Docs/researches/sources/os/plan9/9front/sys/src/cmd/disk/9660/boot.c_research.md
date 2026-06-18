# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/boot.c

El Torito boot support for the ISO 9660 image writer.

Key behavior:
- `Cputbootvol` writes the boot volume descriptor with `EL TORITO SPECIFICATION` and records where the boot catalog block pointer must later be patched.
- `Cupdatebootvol` patches the boot catalog block number into the boot volume descriptor.
- `Cputbootcat` writes the validation entry and records where boot image entries will be patched.
- `Caddbootentry` writes a bootable catalog entry, selecting 1.44MB, 2.88MB, or no-emulation mode and setting load-sector count.
- `Cupdatebootcat` finds BIOS and optional EFI boot image directory entries, writes catalog entries, and emits an EFI section header when both BIOS and EFI images are present.

Notable dependencies:
- Directory lookup via `walkdirec`.
- ISO byte emitters from `cdrdwr.c`.

Research notes:
- Warns when boot images are not encountered or when no-emulation BIOS images exceed the 2KB initial load count.
- Supports both traditional floppy-emulation and no-emulation boot images.
