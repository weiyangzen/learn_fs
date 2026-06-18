# File Research: sources/os/linux/linux/fs/nls/mac-turkish.c

Implements the `macturkish` NLS codepage module.

Key behavior:
- Provides generated mappings for Mac Turkish.
- Extends the Mac Roman-style table with Turkish-specific characters including `011e/011f`, `0130/0131`, and `015e/015f`.
- Includes a private-use mapping at `0xf8a0` and the Apple private-use glyph `0xf8ff`.
- Reverse lookup uses pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, and `f8`.
- Registers charset name `macturkish`.

Important interactions:
- Supplies exact byte/Unicode conversion through the shared `struct nls_table` interface.
- No multibyte state exists; every conversion consumes or emits exactly one byte on success.
