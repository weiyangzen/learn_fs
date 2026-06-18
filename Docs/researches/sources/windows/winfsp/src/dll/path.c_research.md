# File Research: sources/windows/winfsp/src/dll/path.c

Tiny in-place wide-string path helper module for WinFsp DLL code.

Key functions:
- `FspPathPrefix(Path, PPrefix, PRemain, Root)`: splits `Path` at the first backslash, replaces that separator with `NUL`, skips repeated separators, and returns prefix/remainder pointers. If the prefix is the leading root separator and `Root` is supplied, the prefix pointer is replaced with `Root`.
- `FspPathSuffix(Path, PRemain, PSuffix, Root)`: splits at the final path separator, replacing it with `NUL`; handles root specially via `Root`; returns suffix as the final component or the string end if no separator exists.
- `FspPathCombine(Prefix, Suffix)`: restores previously split path separators by converting embedded `NUL` characters between `Prefix` and `Suffix` back to backslashes.

Important behavior:
- All helpers mutate the input path buffer.
- Repeated backslashes after a split separator are skipped.
- Used by security and utility code to temporarily isolate parent/name components without extra allocation.
