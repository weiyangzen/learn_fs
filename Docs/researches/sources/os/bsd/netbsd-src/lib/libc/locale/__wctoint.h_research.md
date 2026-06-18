# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/__wctoint.h

Read completely: 79 lines.

This header defines inline `__wctoint`, mapping wide characters `0-9`, `A-Z`, and `a-z` to digit values `0..35`, returning `-1` for non-digits.

Important interactions: included by the `_wcstol.h` and `_wcstoul.h` templates and their concrete integer conversion wrappers. It deliberately avoids locale-dependent classification.

Security/reliability notes: no allocation or I/O. The conversion is ASCII-style only, which matches base conversion expectations for these libc functions.
