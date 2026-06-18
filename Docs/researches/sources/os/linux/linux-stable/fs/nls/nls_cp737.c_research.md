# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp737.c

Implements Linux NLS support for DOS codepage `cp737`, described as Greek. It is wired by `CONFIG_NLS_CODEPAGE_737` to `nls_cp737.o`.

Key contents:
- `charset2uni[256]` maps ASCII plus Greek letters, box drawing, block, and symbol bytes to Unicode.
- Reverse pages are `page00`, `page03`, `page20`, `page22`, and `page25`.
- `charset2lower` / `charset2upper` encode Greek and ASCII case folding in the original codepage byte space.
- `uni2char()` uses `page_uni2charset` to find exact byte mappings and returns `-EINVAL` for missing mappings.
- `char2uni()` returns one Unicode `wchar_t` per input byte and rejects byte `0x00`.
- Registers `.charset = "cp737"` with module description `NLS Codepage 737 (Greek)`.

Important behavior:
- This module is single-byte only; there is no state machine or multibyte parsing.
- It supports Greek DOS filenames through the standard Linux NLS table API.
- Reverse conversion is intentionally sparse and exact, so Unicode compatibility variants are not folded into approximate cp737 bytes.
