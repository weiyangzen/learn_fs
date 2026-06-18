# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/os.h

Purpose: Platform-selection and base typedef header for the bzip2 library.

Key points:
- Defaults to `BZ_UNIX 1`, with conditional switches for `_WIN32` and `PLAN9`.
- Includes `unix.h`, `lccwin32.h`, or `plan9.h` according to selected platform.
- Defines `NORETURN` for GCC.
- Defines core bzip2 typedefs: `Char`, `Bool`, `UChar`, `Int32`, `UInt32`, `Int16`, `UInt16`, `IntNative`.
- Defines `True` and `False`.

Dependencies and interactions:
- Included by all bzip2 library C files.
- `PLAN9` builds include `plan9.h`; otherwise the default Unix header is used.

Research notes:
- Although this lives in the Plan 9 tree, it keeps upstream multi-platform structure.
- Type size assumptions are centralized here.
