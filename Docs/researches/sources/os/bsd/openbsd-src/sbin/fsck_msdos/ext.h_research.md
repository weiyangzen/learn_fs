# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/ext.h

## Scope

Shared declarations, options, result flags, and module APIs for `fsck_msdos`.

## Main Contents

- Extern options: `alwaysno`, `alwaysyes`, `preen`, `rdonly`, and global disklabel `lab`.
- Result flags: `FSOK`, `FSBOOTMOD`, `FSDIRMOD`, `FSFATMOD`, `FSERROR`, `FSFATAL`.
- Public APIs for boot, FAT, directory, lost-chain, prompt, and helper operations.
- Defines `LOSTDIR` as `LOST.DIR`.

## Dependencies

Includes `dosfs.h` and shared `fsutil.h`.

## Risks And Edge Cases

The return flags are bitmasks that represent both fatality and modification categories; callers must preserve and test combinations carefully.
