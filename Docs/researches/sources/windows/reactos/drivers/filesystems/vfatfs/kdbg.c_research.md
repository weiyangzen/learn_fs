# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/kdbg.c

## Purpose

`kdbg.c` implements optional KDBG command support for inspecting VFAT state at runtime. The whole command handler is compiled only under `KDBG`.

## Commands

- `?fat.vols`
  - Walks `VfatGlobalData->VolumeListHead`.
  - Prints each mounted volume device pointer and VCB pointer.
  - Reports when no volume is found.
- `?fat.files <volume-or-vcb-pointer>`
  - Matches the argument against either a VCB pointer or volume device pointer formatted with `%p`.
  - Walks the matching volume's `FcbListHead`.
  - Prints FCB pointer, reference count, open count, cleanup/close/delayed-close flags, backing file object, and path.
- `?fat.setdbgfile [path]`
  - With no path, frees and clears the global `DebugFile`.
  - With a path, converts an ANSI argument to a Unicode string and stores it in `DebugFile`.

## Important Details

- The handler only claims commands beginning with `?fat.`.
- It uses `DPRINT1` for debugger-visible output.
- It does not acquire the global volume-list resource or per-volume FCB-list locks while walking state, so it is a diagnostic aid rather than synchronized production logic.

## Research Notes

This file is useful when tracing FCB lifetime bugs because the printed flags line up with KDBG-only FCB flags declared in `vfat.h`.
