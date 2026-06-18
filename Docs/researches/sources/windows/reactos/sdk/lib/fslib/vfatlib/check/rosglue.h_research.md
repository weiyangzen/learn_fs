# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/rosglue.h

Adapts imported checker code to the ReactOS runtime.

Key elements:
- Defines `__attribute__` away for non-GNU compilers, with a packing warning.
- Remaps `printf` to `VfatPrint`.
- Remaps allocation calls to `vfalloc`, `vfcalloc`, and `vffree`.
- Defines `FSCHECK_*` bit flags and maps traditional dosfsck globals to `FsCheckFlags`, `FsCheckTotalFiles`, and `FsCheckMemQueue`.
- Forces `atari_format` to `FALSE`.

Dependencies:
- Expects globals and print/allocation functions from the ReactOS VFAT library/checker integration.

Research notes:
- This is the main compatibility layer that lets dosfstools-derived code compile in ReactOS user-mode filesystem libraries.
- Because `interactive`, `rw`, and related names are macros, side effects depend on global `FsCheckFlags`.
