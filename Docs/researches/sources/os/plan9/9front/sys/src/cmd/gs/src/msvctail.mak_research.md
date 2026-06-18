# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvctail.mak

## Purpose
Common tail fragment for MSVC/NMAKE Ghostscript builds, focused on auxiliary tools and common Windows library response files.

## Main Structure
- Rule for `ccf32.tr` creates generated/object/bin directories and writes common preprocessor flags.
- Builds auxiliary generators: `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Has special 64-bit `genarch` path using separate compile/link steps.
- Defines `LIBCTR` response file with common Windows libraries.

## Integration Notes
- Included after `msvccmd.mak` and platform variables are established.
- Supports both full Windows and library-only builds.

## Risks and Edge Cases
- Directory creation is tied to the first generation of `ccf32.tr` as a workaround for NMAKE lacking `.BEFORE`.
- Common libraries are hard-coded: `shell32`, `comdlg32`, `gdi32`, `user32`, `winspool`, `advapi32`.
