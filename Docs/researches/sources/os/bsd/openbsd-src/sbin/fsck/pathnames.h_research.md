# File Research: sources/os/bsd/openbsd-src/sbin/fsck/pathnames.h

Defines fsck helper search directories:
- `_PATH_SBIN` as `/sbin`
- `_PATH_USRSBIN` as `/usr/sbin`

`fsck.c` uses these paths when locating and execing filesystem-specific helper programs named `fsck_<fstype>`.
