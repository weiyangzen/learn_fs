# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp852.c

Implements Linux NLS support for DOS codepage `cp852`, described as Central/Eastern Europe. It is built as `nls_cp852.o` under `CONFIG_NLS_CODEPAGE_852`.

Key contents:
- `charset2uni[256]` maps cp852 bytes to Latin-2/Central European Unicode characters and DOS graphics.
- Reverse pages are `page00`, `page01`, `page02`, and `page25`.
- `page02` is notable for combining/extended Latin codepoints used by this Central/Eastern European codepage.
- `charset2lower` and `charset2upper` provide ASCII and regional Latin case folding.
- `uni2char()` and `char2uni()` use the same one-byte exact conversion pattern as the neighboring codepage modules.
- Registers `.charset = "cp852"`.

Important behavior:
- Intended for DOS filenames using Central/Eastern European encodings.
- The file has no runtime allocation or mutable state; all conversion behavior is compiled-in table data.
