# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/windows_.h

Ghostscript wrapper for `windows.h`.

Key points:
- Defines `STRICT` before including `<windows.h>`.
- For Watcom, defines `LPRGBQUAD` and adapts `BEGIN_THREAD` to Watcom’s `_beginthread(proc, NULL, stksize, data)` signature.
- For non-Watcom builds, defines `BEGIN_THREAD` with the usual `_beginthread(proc, stksize, data)` signature.
- Provides null Win32 equivalents for Watcom 32-to-16-bit glue helpers such as `AllocAlias16`, `FreeAlias16`, `MK_FP16`, `MK_FP32`, `GetProc16`, and `ReleaseProc16`.
- Under Win32, maps `_fstrtok` to `strtok`.
- For Borland C, maps `exception_code()` to `__exception_code`.

Dependencies and interactions:
- Included by Windows platform and interpreter code.
- Abstracts compiler-specific Windows API and threading differences.

Research relevance:
- Small portability wrapper for Windows compiler/runtime quirks.
