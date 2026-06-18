# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp775.c

Implements Linux NLS support for DOS codepage `cp775`, described as Baltic Rim. It is built from `CONFIG_NLS_CODEPAGE_775`.

Key contents:
- `charset2uni[256]` maps cp775 bytes to Unicode, covering Baltic accented Latin characters plus DOS drawing symbols.
- Reverse pages are `page00`, `page01`, `page20`, `page22`, and `page25`.
- `charset2lower` and `charset2upper` define case folding for ASCII and cp775-specific Latin letters.
- `page_uni2charset` maps Unicode high bytes `00`, `01`, `20`, `22`, and `25` to their reverse tables.
- `uni2char()` checks output capacity, emits one byte for exact mappings, and rejects unmapped Unicode.
- `char2uni()` returns one Unicode value per byte and treats `0x0000` as invalid.
- Registers `.charset = "cp775"`.

Important behavior:
- The file is pure generated data plus standard NLS glue.
- It is used where filesystems need Baltic DOS filename conversion, especially FAT-family mounts configured with this codepage.
