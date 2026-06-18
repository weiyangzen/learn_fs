# File Research: sources/os/linux/linux/fs/nls/nls_cp1250.c

Implements the `cp1250` Windows Central European NLS codepage module.

Key behavior:
- Provides generated Windows CP1250 mappings for Central European and Slavic Latin characters.
- `charset2uni` includes undefined CP1250 bytes as `0x0000`, which `char2uni()` rejects.
- Reverse lookup uses pages `00`, `01`, `02`, `20`, and `21`.
- Case tables include ASCII and CP1250-specific upper/lower mappings for accented Latin letters.
- Registers charset name `cp1250`.

Important interactions:
- Used by filesystems that expose or consume CP1250-encoded filenames.
- Exact reverse mappings mean Unicode characters without a CP1250 byte fail instead of being approximated.
