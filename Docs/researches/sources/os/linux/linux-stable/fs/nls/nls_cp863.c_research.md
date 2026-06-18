# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp863.c

Implements Linux NLS support for DOS codepage `cp863`, described as Canadian French. It is built by `CONFIG_NLS_CODEPAGE_863`.

Key contents:
- `charset2uni[256]` maps Canadian French DOS bytes to Unicode, including accented Latin letters and DOS graphic symbols.
- Reverse pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- Case tables define ASCII and cp863-specific accented case folding.
- `uni2char()` performs sparse exact reverse conversion.
- `char2uni()` performs direct byte-to-Unicode table lookup.
- Registers `.charset = "cp863"`.

Important behavior:
- Intended for legacy Canadian French DOS/FAT filename conversion.
- It is a generated, data-heavy module with the same error semantics as the other single-byte NLS codepages.
