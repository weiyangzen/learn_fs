# File Research: sources/os/bsd/netbsd-src/lib/libedit/chartype.h

This internal header defines libedit's character conversion buffer and wide-character display APIs.

Key declarations:
- `ct_buffer_t` holds reusable narrow and wide buffers plus their sizes.
- Encoding/decoding APIs for strings, argv arrays, and single characters.
- Visual-width and visual-rendering APIs.
- Character classification constants and `ct_chr_class()`.

Portability checks:
- Verifies, on many non-BSD platforms, that `wchar_t` stores ISO 10646 characters.
- Warns when `WCHAR_MAX < INT32_MAX`, indicating no non-BMP support.

Important constants:
- `VISUAL_WIDTH_MAX` is 8, enough for the widest `\U+nnnnn` representation used here.
- `MB_FILL_CHAR` marks terminal cells occupied by the extra width of a wide character.
- Character class constants distinguish printable, ASCII control, tab, newline, and nonprintable cases.

Integration:
- Included by `el.h`, so conversion/display helpers are core to all line editing and refresh paths.
