# File Research: sources/os/linux/linux-stable/fs/nls/mac-roman.c

This file implements the Linux NLS module for classic Macintosh Roman, registered as `macroman`.

It is a generated mapping module for the base Mac Roman repertoire. `charset2uni[256]` preserves the lower ASCII/control range and maps high bytes to Western European accented Latin letters, punctuation, mathematical symbols, the Euro sign, Apple private-use `0xf8ff`, and ligatures `U+FB01`/`U+FB02`. Reverse lookup spans Unicode pages `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, `pagef8`, and `pagefb`.

The implementation surface is the usual NLS table contract:
- `uni2char()` maps a Unicode `wchar_t` to a one-byte codepage value via `page_uni2charset`.
- `char2uni()` maps one input byte through `charset2uni`.
- Both reject unmappable values with `-EINVAL`; `uni2char()` also returns `-ENAMETOOLONG` for zero output capacity.
- `struct nls_table table` exposes the callbacks and case tables under `.charset = "macroman"`.

This is the broadest Mac table in this group because it includes the extra ligature reverse page `pagefb`. Like the related generated Mac modules, `charset2lower` and `charset2upper` are filled with `0xff`, so the file does not provide meaningful case conversion even though the fields are wired into the table.

The module uses standard init/exit registration and declares `MODULE_DESCRIPTION("NLS Codepage macroman")`, `MODULE_LICENSE("Dual BSD/GPL")`, and the Unicode data permission notice.
