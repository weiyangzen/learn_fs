# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/Makefile.inc

Libc build fragment for the Citrus internationalization subsystem.

Key behavior:
- Adds the Citrus source directory to `.PATH`.
- Reads the i18n module shared-library major version and defines `I18NMODULE_MAJOR` for `citrus_module.c`.
- Adds core Citrus sources, locale-category loaders, converter/mapper/database helpers, and ctype support to libc.
- Adds include paths for shared `_strtol.h`/`_strtoul.h` templates and locale internals.
- Suppresses format-truncation warnings for `citrus_iconv.c` and `citrus_csmapper.c`, both of which assemble bounded path/key strings.

This file defines the compilation surface for the non-module Citrus runtime embedded in libc.
