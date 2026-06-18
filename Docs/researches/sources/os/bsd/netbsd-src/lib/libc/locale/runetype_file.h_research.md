# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_file.h

Read completely: 136 lines.

This header defines the serialized rune locale file format and runetype bit masks. It declares packed file entries/ranges/locales, magic string `RuneCT10`, the `CODESET=` variable tag, cached table sizes, rune scalar types, and screen-width/type flags.

Important interactions: `rune.c` reads these packed structures from mapped locale files and converts them to host-endian `_RuneLocale` structures. Tools that generate locale files must match this layout.

Security/reliability notes: serialized fields are network-endian and packed. Consumers must validate lengths carefully before accessing trailing variable-size data.
