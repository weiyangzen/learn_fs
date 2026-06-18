# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/windows_.h

Ghostscript wrapper around `<windows.h>`.

Key points:
- Defines `STRICT` before including Windows headers.
- For Watcom, defines `LPRGBQUAD` and adapts `BEGIN_THREAD` to Watcom’s `_beginthread` signature with an extra stack-bottom argument.
- For non-Watcom, defines null equivalents of Watcom 32-to-16-bit glue macros such as `AllocAlias16`, `FreeAlias16`, `MK_FP16`, `MK_FP32`, `GetProc16`, and `ReleaseProc16`.
- For Win32, maps `_fstrtok` to `strtok`.
- For Borland C, maps `exception_code()` to `__exception_code`.

Dependencies and interactions:
- Included by Windows platform code and makefile dependency rules.
- Supports MSVC, Borland, and Watcom differences.

Research relevance:
- Small but central Windows portability wrapper for compiler and 16/32-bit compatibility differences.
