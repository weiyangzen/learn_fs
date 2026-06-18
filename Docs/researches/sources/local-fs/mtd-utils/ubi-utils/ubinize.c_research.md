# File Research: sources/local-fs/mtd-utils/ubi-utils/ubinize.c

## Purpose
Implements `ubinize`, the UBI image generator. It reads an INI configuration describing UBI volumes and writes a complete UBI image for flash geometry supplied on the command line.

## Main Entry Points
- `parse_opt()` parses output path, PEB size, min I/O size, sub-page size, VID header offset, erase counter, UBI version, image sequence, and verbosity.
- `read_section()` parses one INI section into `struct ubigen_vol_info`, including mode, type, image file, volume ID, size, name, alignment, flags, and derived LEB usage.
- `main()` initializes ubigen geometry, creates the volume table, reads all INI sections, writes each volume image, and finally writes the layout volume.

## Control Flow
The program requires an output file, physical eraseblock size, minimum I/O size, and one INI file. It seeds a default random image sequence, validates flash geometry, initializes `struct ubigen_info`, creates an empty volume table, then loads the INI file with `iniparser`.

Each section must have `mode=ubi`; non-UBI sections are skipped. For UBI sections, `read_section()` defaults absent volume type to dynamic, requires an image for static volumes, requires `vol_id` and `vol_name`, derives `vol_size` from the image when omitted, validates image size against volume size, handles `vol_flags=autoresize`, and computes data padding, usable LEB size, and used eraseblocks. `main()` enforces unique volume IDs and names and only one autoresize volume, adds each volume to the volume table, writes image-backed volume data after the first two PEBs, then writes the layout volume at the front.

## Dependencies
Depends on Linux UBI media definitions, `libubigen` for image/layout writing, `libiniparser` for configuration parsing, `libubi` constants, POSIX file/stat APIs, and local `common.h` plus `ubiutils-common.h`.

## Risks and Notes
The VID-header offset validation message says it must be a multiple of the min I/O unit, but the code checks only `% 8`. In `read_section()`, the negative alignment check tests `vi->id < 0` instead of `vi->alignment < 0`, so a negative `vol_alignment` from the INI may pass local validation. If a second autoresize volume is found, the code returns immediately from inside the loop, bypassing normal cleanup of allocated structures, open output, and temporary output removal.
