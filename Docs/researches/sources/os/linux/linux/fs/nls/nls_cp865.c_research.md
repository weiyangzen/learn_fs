# File Research: sources/os/linux/linux/fs/nls/nls_cp865.c

Implements Linux NLS support for codepage 865, described as Norwegian/Danish. It is a generated DOS/OEM charset module.

The forward table maps low bytes to ASCII/control values and high bytes to Nordic/Western Latin characters, DOS box/block drawing, Greek/math symbols, and related punctuation. Reverse Unicode pages are `00`, `01`, `03`, `20`, `22`, `23`, and `25`, very similar in shape to CP437/CP861 but with Nordic-specific byte assignments.

`uni2char()` checks buffer capacity and uses sparse reverse pages for exact mappings only. `char2uni()` maps one byte to a `wchar_t` and rejects `0x0000`.

The module registers charset `"cp865"` with CP865-specific casefold arrays. Init/exit call `register_nls()` and `unregister_nls()`. Metadata identifies `NLS Codepage 865 (Norwegian, Danish)` and `Dual BSD/GPL`.
