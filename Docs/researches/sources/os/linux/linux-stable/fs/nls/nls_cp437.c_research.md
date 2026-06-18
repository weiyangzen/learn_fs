# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp437.c

Implements Linux NLS support for DOS codepage `cp437`, described as United States/Canada. The module is selected by `CONFIG_NLS_CODEPAGE_437` and built as `nls_cp437.o`.

Key contents:
- `charset2uni[256]` at line 16 maps each cp437 byte to a plane-0 `wchar_t`.
- Reverse Unicode-to-byte pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`; `page_uni2charset` indexes those by Unicode high byte.
- `charset2lower` and `charset2upper` implement cp437-aware case conversion, including ASCII and selected accented/Greek entries.
- `uni2char()` rejects zero output space with `-ENAMETOOLONG`, then uses the sparse page table; unmapped Unicode returns `-EINVAL`.
- `char2uni()` maps one input byte through `charset2uni`; byte `0x00` maps to `0x0000` and is treated as invalid.
- Registers `.charset = "cp437"` and exports lower/upper tables through `struct nls_table`.

Important behavior:
- This is a table-only, stateless converter for filenames and other filesystem strings using DOS cp437.
- Only exact mappings from Unicode to cp437 are accepted.
- NUL is not represented by `char2uni()`/`uni2char()` success paths; callers rely on NLS helper conventions for terminators.
