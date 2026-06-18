# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mkdev.h

Purpose: Defines device major/minor bit sizes and userland device-number construction/extraction interfaces.

Key definitions:
- SVR3/pre-EFT major/minor sizes and maxima.
- 32-bit Solaris device major/minor sizes: 14/18 bits.
- 64-bit Solaris device major/minor sizes: 32/32 bits.
- Native `NBITSMAJOR`, `NBITSMINOR`, `MAXMAJ`, `MAXMIN` selected by `_LP64`.

Userland interfaces:
- `makedev()`, `major()`, `minor()` and underlying `__makedev()`, `__major()`, `__minor()`.
- Format selectors: `OLDDEV`, `NEWDEV`, `COMPATDEV`.

Important detail: In non-kernel builds it undefines possible `sysmacros.h` macros before declaring the illumos functions/macros.

Relevance to subset A: Device-number ABI used by filesystems, mount tables, device nodes, and drivers.
