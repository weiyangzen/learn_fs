# File Research: sources/os/linux/linux/fs/nls/nls_cp864.c

Implements Linux NLS support for codepage 864, described as Arabic. It is a generated exact mapping table module.

Unlike most surrounding DOS codepages, CP864 maps some printable low-range bytes to Arabic-related symbols, including `0x25` to U+066A. The high byte range includes Arabic letters and presentation forms, plus Greek/math and box/block drawing entries. Reverse Unicode pages are `00`, `03`, `06`, `22`, `25`, and `fe`; page `06` covers Arabic, and page `fe` covers Arabic presentation forms.

`uni2char()` performs sparse exact reverse lookup and returns `-EINVAL` for unsupported Unicode. `char2uni()` maps one byte through the forward table and rejects `0x0000`, which also filters undefined CP864 byte positions.

The registered charset is `"cp864"` with byte-oriented lower/upper tables. Init and exit use the normal NLS registration lifecycle. Metadata is `NLS Codepage 864 (Arabic)` under `Dual BSD/GPL`.
