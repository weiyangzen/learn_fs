# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.h

Public internal wrapper for Citrus iconv handles.

Key behavior:
- Declares `_citrus_iconv_open` and `_citrus_iconv_close`.
- Includes local ABI definitions.
- Defines `_CITRUS_ICONV_F_HIDE_INVALID`.
- Provides inline `_citrus_iconv_convert` dispatch to the module's `io_convert`.

The actual conversion implementation is module-provided; this header supplies the stable call surface.
