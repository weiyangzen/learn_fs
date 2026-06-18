# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dosboot.c

## Purpose
Minimal read-only FAT12/FAT16/FAT32 filesystem implementation used by the bootstrap loader to read `plan9.ini` and kernel files.

## Main Interfaces
- Exports `dosinit(Bootfs*, char*)`.
- Exports `dosread`, `doswalk`, `dosdirread`, and `dosreadseg`.

## Implementation Notes
- Maintains a 16-entry cluster cache keyed by `Dos*` and sector.
- `getclust` reads clusters from the underlying `Bootfs` device channel using `myreadn`.
- `fatwalk` decodes FAT12, FAT16, or FAT32 chain entries and recognizes end-of-chain markers.
- `fileaddr` maps logical file clusters to physical sectors, with special contiguous handling for FAT12/16 root directories.
- `dosread` reads file bytes cluster-by-cluster, respecting file length for non-directories.
- `doswalk` converts a path component into 8.3 uppercase form and scans directory entries.
- `dosdirread` builds a lower-case file-name array from directory entries.
- `dosinit` validates the boot-sector jump, parses BPB fields, determines FAT type, computes FAT/root/data addresses, and initializes `Bootfs.root`, `read`, and `walk`.

## Dependencies And Risks
- Long filenames are not supported; only 8.3 names are recognized.
- FAT heuristics reject unreasonable BPBs but are intentionally small.
- The cluster cache allocation path does not free buffers in this boot-only environment.
