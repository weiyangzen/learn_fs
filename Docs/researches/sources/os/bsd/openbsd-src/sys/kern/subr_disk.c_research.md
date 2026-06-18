# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_disk.c

## Role

Provides OpenBSD disk subsystem support: disklabel checksum/validation, DOS/GPT/FAT partition spoofing, disk attach/detach bookkeeping, open masks, transfer bounds checks, disk accounting, root/swap selection, DUID formatting/mapping, and disk label reads.

## Key Behavior

- `dkcksum()`, `initdisklabel()`, `checkdisklabel()`, and `setdisklabel()` initialize, validate, byte-swap, constrain, checksum, and install OpenBSD disklabels.
- `readdisksector()` and `readdoslabel()` read sector data, synthesize labels from GPT/MBR/FAT, locate OpenBSD label offsets, and then validate on-disk labels when present.
- GPT helpers validate protective MBRs, read and checksum GPT headers/partition arrays, map known GPT UUIDs to OpenBSD fstypes, and expose non-OpenBSD partitions beginning at label partition `i`.
- MBR helpers walk primary and extended partitions, identify OpenBSD A6 partitions, set label bounds, and expose supported foreign partitions.
- `bounds_check_with_label()` rejects malformed or misaligned transfers, returns EOF at partition end, and truncates transfers that extend past a partition.
- `disk_init()`, `disk_construct()`, `disk_attach()`, `disk_attach_callback()`, and `disk_detach()` manage global disk lists, labels, attach timestamps, device numbers, asynchronous label reads, randomness seeding, and softraid attach notifications.
- `disk_openpart()` and `disk_closepart()` maintain block/character/open partition masks to protect open partitions from unsafe relabeling.
- `disk_busy()` and `disk_unbusy()` maintain busy time, transfer counters, seek counts, and entropy contributions.
- `setroot()`, `getdisk()`, `parsedisk()`, and `dk_mountroot()` choose root/swap/dump devices, support askname prompts, DUID-root mapping, NFS boot handling, and filesystem-specific mountroot dispatch.
- `disk_readlabel()`, `disk_map()`, `disk_lookup()`, `duid_equal()`, `duid_iszero()`, and `duid_format()` provide label and DUID utility services.

## Interfaces And Dependencies

Depends on disklabel macros, vnode block/character device operations, `bdevsw`/`cdevsw`, GPT/MBR structures, zlib CRC32, softraid hooks, root/swap globals, autoconf device lists, and filesystem mountroot entry points.

## Notes

This is one of the subset’s storage-relevant kernel files. It bridges physical/media partition metadata with OpenBSD’s disklabel model and boot-time root selection. Label bounds and raw partition preservation are intentionally enforced after reading or setting labels.
