# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/localeio.h

Read completely: 36 lines.

This header declares locale file I/O helpers: `_localeio_map_file`, `_localeio_unmap_file`, and `__loadlocale`.

Important interactions: category loaders and rune loading paths use these helpers to map and load external locale files.

Security/reliability notes: declaration-only header. The interface passes raw mapped memory and sizes, so callers must validate file formats.
