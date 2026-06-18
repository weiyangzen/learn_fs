# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/check.c

## Scope

Top-level filesystem check sequence for `fsck_msdos`.

## Main APIs

- `checkfilesys(fname)` opens the device, reads disklabel and boot metadata, reads/compares FATs, checks FAT chains, scans directories, handles lost chains, writes modifications, and returns fsck exit status.
- Defines global `struct disklabel lab`.

## Control Flow

The checker unveils `/dev`, opens read-write unless forced read-only by `alwaysno`, falls back to read-only if necessary, prints device identity, reads disklabel, pledges `stdio`, and calls `readboot()`.

It reads the selected FAT or FAT 0, compares other FATs when mirroring is active, validates cluster chains through `checkfat()`, writes FAT modifications when needed, initializes directory-scan state, scans directory trees, handles lost chains, writes final FAT changes, frees state, and reports file/free/bad cluster statistics.

Exit status is `8` for fatal/unrecovered errors, `4` when modified, and `0` when clean.

## Dependencies

- Uses `readboot()`, `readfat()`, `comparefat()`, `checkfat()`, `writefat()`, `resetDosDirSection()`, `handleDirTree()`, `checklost()`.
- Uses shared `fsutil` device helpers and prompt/error functions.

## Risks And Edge Cases

- Directory scan can modify FAT state, so the code writes FATs both before and after directory processing.
- `rdonly = alwaysno` forces no-write behavior for no-answer mode.
- FAT32 non-mirrored mode reads only `ValidFat`; mirrored mode compares all FAT copies.
