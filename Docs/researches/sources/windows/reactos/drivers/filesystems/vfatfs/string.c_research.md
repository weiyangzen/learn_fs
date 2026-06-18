# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/string.c

## Purpose

`string.c` provides small VFAT pathname/name validation helpers.

## Contents

- `long_illegals` lists characters invalid in long filenames: `"*\\<>/?:|`.
- `vfatIsLongIllegal(WCHAR c)` returns whether a character appears in that invalid-character set.
- `IsDotOrDotDot(PCUNICODE_STRING Name)` returns true for the single-component names `.` and `..`.

## Research Notes

Despite its `PURPOSE` comment saying "Volume routines", this file is a name-helper module. The prototype for `vfatSplitPathName()` is in `vfat.h`, but that function is not implemented in this file.
