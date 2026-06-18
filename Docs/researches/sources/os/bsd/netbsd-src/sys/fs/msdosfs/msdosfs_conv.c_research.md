# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_conv.c

## Purpose
Implements FAT timestamp conversion, DOS 8.3 filename conversion, Win95 long filename conversion, UCS-2/UTF-8/8-bit helpers, and case-insensitive name matching.

## Main Entry Points
- `msdosfs_unix2dostime()` converts Unix `timespec` plus GMT offset to DOS date/time/hundredths fields, clamping invalid pre-1980 or too-future dates to zero.
- `msdosfs_dos2unixtime()` converts DOS date/time/hundredths fields back to Unix `timespec`.
- `msdosfs_dos2unixfn()` converts 8.3 DOS names to Unix names using translation and lowercase tables.
- `msdosfs_unix2dosfn()` converts Unix names to short 8.3 names, handles `.`/`..`, trims trailing dots/blanks, rejects all-dot/all-blank names, and adds `~N` generation suffixes.
- `msdosfs_unix2winfn()` creates a Win95 long-name slot from a Unix name segment.
- `msdosfs_winChkName()` verifies a long-name slot against a Unix name and checksum.
- `msdosfs_win2unixfn()` converts long-name slots into a `dirent` name, prepending segments read in reverse order.
- `msdosfs_winChksum()` computes the long-name checksum over the short 8.3 name.
- `msdosfs_winSlotCnt()` computes the number of long-name slots required.
- Static helpers convert between UCS-2 and UTF-8 or 8-bit strings, pad UCS-2 long-name buffers, fold Unicode with `msdosfs_unicode_foldmap`, and compare names case-insensitively.

## Dependencies
Uses NetBSD clock conversion helpers, endian helpers, dirent/vnode context in kernel builds, libc equivalents for tools, and declarations from `direntry.h` and `denode.h`.

## Risks and Notes
The UTF-8 decoder accepts multibyte sequences without validating continuation-byte shape or overlong forms. Several string length helpers are called with `out == NULL` to measure lengths, but internally subtract pointers derived from `NULL`, which is undefined C even if it works on common compilers. `msdosfs_win2unixfn()` explicitly notes that long UCS-2 names can be silently truncated to fit `dirent.d_name`, potentially creating indistinguishable names. The code supports UCS-2, not full UTF-16 surrogate pairs.
