# File Research: sources/os/bsd/dragonflybsd/sys/sys/iconv.h

`iconv.h` defines kernel iconv character-set conversion constants, sysctl ABI structures, userland management functions, and kernel converter/module interfaces.

Shared definitions include charset/converter name length limits, maximum charset-pair data length, xlat16 flags, case-conversion flags, Unicode/wctype names, `iconv_cspair_info`, `iconv_add_in`, and `iconv_add_out`. Userland declarations cover adding xlat tables/pairs, converter and charset lookup, and charset quirk handling.

Under `_KERNEL`, it defines converter classes, charset-pair records, module declaration macros for converters and CES modules, core conversion APIs, case conversion APIs, filesystem iconv bridge declarations via `VFS_DECLARE_ICONV`, lookup/helper functions, module handlers, and debug macros.
