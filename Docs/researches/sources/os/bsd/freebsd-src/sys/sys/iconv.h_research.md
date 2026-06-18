# File Research: sources/os/bsd/freebsd-src/sys/sys/iconv.h

Defines FreeBSD kernel iconv charset conversion limits, flags, sysctl ABI structs, user helper declarations, and kernel converter-class infrastructure. Charset and converter names are capped at 31 bytes, and conversion pair metadata is surfaced through versioned structs.

For userland, it declares functions such as `kiconv_add_xlat_table`, `kiconv_add_xlat16_*`, `kiconv_lookupconv`, `kiconv_lookupcs`, and charset quirk lookup. For kernel builds, it includes kobj/module/queue/sysctl dependencies and defines `struct iconv_converter_class`, `struct iconv_cspair`, and module declaration macros for converters and CES modules.

The kernel API includes open/close/convert functions, case-aware conversion, string/memory conversion helpers, VFS iconv bridge module support via `VFS_DECLARE_ICONV`, and internal converter stubs. Filesystems using on-disk encodings depend on this as a conversion plug-in interface.
