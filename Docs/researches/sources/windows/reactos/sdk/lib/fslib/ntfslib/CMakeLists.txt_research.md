# File Research: sources/windows/reactos/sdk/lib/fslib/ntfslib/CMakeLists.txt

This build file defines the NTFS filesystem library target.

Contents:
- Builds `ntfslib` from `ntfslib.c`.
- Adds a dependency on `psdk`.

Risk points:
- The resulting library exports only stubs from the current source file.
- No formatting/checking implementation sources are included.
