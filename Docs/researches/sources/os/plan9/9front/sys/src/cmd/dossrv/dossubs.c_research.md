# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dossubs.c

## Purpose
Contains most FAT filesystem logic for `dossrv`: format detection, BPB parsing, cluster-chain management, directory traversal, long-name handling, file I/O, allocation, truncation, and metadata conversion.

## Key Behavior
- `isdosfs()` recognizes FAT boot-sector jump signatures, including dynamic disk manager cases.
- `dosfs()` reads the boot sector, validates sector geometry, detects FAT12/16/32, populates `Dosbpb`, handles FAT32 active-FAT mirroring flags, reads FAT32 info sector free-space hints, and computes root/data/FAT geometry.
- `rootfile()`, `getfile()`, and `putfile()` manage the synthetic root and held sector for the current DOS directory entry.
- `fileclust()` walks or extends a file’s cluster chain, using contiguous allocation for DOS system files.
- `fileaddr()` translates a file-relative sector number to an absolute filesystem sector, with special handling for FAT12/16 fixed root directories and FAT32 root cluster.
- Name helpers classify Plan 9 names as invalid, valid 8.3, lower-case 8.3, or long; generate `~N` aliases; normalize optional colon/space translation; and validate Plan 9 path elements.
- `searchdir()` scans a directory for a name or for free slots, assembling long filename sequences, checking alias checksums, and reserving enough entries for long names across sector boundaries.
- `readdir()` emits Plan 9 stat records while skipping deleted, volume-label, and `.`/`..` entries and preferring valid long names over short aliases.
- `walkup()` reconstructs a parent directory pointer by using `.`/`..` entries and scanning the grandparent directory for the parent’s start cluster.
- `readfile()` and `writefile()` perform sector-by-sector file data access, allocating clusters on writes and updating file length/time.
- `truncfile()` frees cluster chains beyond the requested length and updates file length/start state.
- `getdir()` and `putdir()` translate DOS attributes, qids, length, and timestamps to/from Plan 9 `Dir` fields.
- Long filename helpers decode and encode UTF-16LE directory slots, maintain checksum/order validation, and support names up to `DOSNAMELEN`.
- FAT helpers `getfat()` and `putfat()` read/write 12-, 16-, and FAT32 28-bit entries across sector boundaries and across mirrored FAT copies; `putfat()` also updates FAT32 info-sector counters when present.
- Allocation helpers `falloc()`, `ffree()`, `cfalloc()`, `iscontig()`, and `makecontig()` find free clusters, zero new clusters, and relocate files to make system files contiguous with spare growth space.
- Time helpers convert between DOS date/time fields and Plan 9 seconds using local timezone rules.
- Debug dump functions print boot sectors, FAT32 info/backup sectors, and directory entries when `chatty` is enabled.

## Interfaces And Dependencies
- Called from `dosfs.c`, `xfile.c`, and other dossrv support modules through prototypes in `fns.h`.
- Uses sector cache APIs from `iotrack.c` and raw device I/O from `devio.c`.
- Relies on `Dosbpb`, `Dosptr`, `Xfs`, and `Xfile` definitions from `dat.h`.

## Notes
This file is the behavioral core of FAT support. Its riskiest paths are metadata mutation paths that span multiple structures: long-name creation/removal, rename, FAT mirroring, FAT12 boundary writes, and contiguous-file relocation.
