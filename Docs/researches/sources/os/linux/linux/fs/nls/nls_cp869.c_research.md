# File Research: sources/os/linux/linux/fs/nls/nls_cp869.c

Implements Linux NLS support for codepage 869, described as Greek. It is a generated exact mapping module distinct from CP737 by its byte assignments and Greek coverage.

`charset2uni[256]` maps lower bytes to ASCII/control values and high bytes to Greek letters/diacritics, selected Latin/symbol entries, and DOS box/block drawing. Reverse Unicode pages are `00`, `03`, `20`, and `25`, covering Latin-1/symbols, Greek, punctuation, and box drawing.

`uni2char()` uses sparse reverse pages and returns `-EINVAL` for Unicode characters without an exact CP869 byte. `char2uni()` maps one raw byte and treats `0x0000` as invalid.

The registered table uses charset `"cp869"` with CP869 lower/upper maps. Init and exit use standard NLS registration. Metadata identifies `NLS Codepage 869 (Greek)` and `Dual BSD/GPL`.
