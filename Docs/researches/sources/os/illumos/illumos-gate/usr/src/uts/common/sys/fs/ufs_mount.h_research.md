# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_mount.h

## Role

Defines UFS mount argument and option flag constants.

## Key Interfaces

- `struct ufs_args` carries mount `flags`.
- Mount flags include:
  - `UFSMNT_NOINTR`
  - `UFSMNT_SYNCDIR`
  - `UFSMNT_NOSETSEC`
  - `UFSMNT_LARGEFILES`
  - `UFSMNT_NOATIME`
  - `UFSMNT_NODFRATIME`
  - on-error actions: panic, lock, umount
  - direct I/O controls: disable directio, force directio, no force directio
  - `UFSMNT_LOGGING`

## String Constants

Defines user-facing on-error action names: `"panic"`, `"lock"`, and `"umount"`.

## Risk Notes

These flags are user/kernel mount ABI and feed `ufsvfs` policy. Conflicting direct I/O and error-action flags must be resolved by mount code, not this header.
