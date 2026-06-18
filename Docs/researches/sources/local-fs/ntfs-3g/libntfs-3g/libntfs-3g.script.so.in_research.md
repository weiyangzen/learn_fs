# File Research: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.script.so.in

## Purpose
Linker script template for locating the actual `libntfs-3g.so`.

## Contents
Contains:
- `@OUTPUT_FORMAT@`
- `GROUP ( @rootlibdir@/libntfs-3g.so )`

## Integration Points
Used by the build/install process to emit a linker script that redirects linking to the library in `rootlibdir`.

## Risks
Depends entirely on correct configure-time substitution of output format and root library directory.
