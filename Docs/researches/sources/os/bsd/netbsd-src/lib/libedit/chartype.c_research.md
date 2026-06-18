# File Research: sources/os/bsd/netbsd-src/lib/libedit/chartype.c

This file implements wide-character/multibyte conversion and display-width helpers for libedit.

Key functions:
- `ct_encode_string()` converts wide strings to multibyte strings using a growable `ct_buffer_t`.
- `ct_decode_string()` converts multibyte strings to wide strings.
- `ct_decode_argv()` decodes a narrow argv array into a wide argv array using shared conversion storage.
- `ct_enc_width()` returns the encoded byte width of one wide character.
- `ct_encode_char()` encodes one wide character to a provided byte buffer.
- `ct_visual_string()` converts a string to its printable visual representation.
- `ct_visual_width()` computes display width for control, tab, newline, printable, and nonprintable characters.
- `ct_visual_char()` renders one character as printable/wide display text.
- `ct_chr_class()` classifies a character as printable, ASCII control, tab, newline, or nonprintable.

Important behavior:
- Conversion buffers grow in `CT_BUFSIZ` increments.
- ASCII control characters render as caret notation.
- Nonprintable characters render as `\U+` hexadecimal forms.
- Printable width is delegated to `wcwidth()`.

Risks and notes:
- Conversion uses process locale functions such as `mbstowcs()`, `wctomb()`, and `wcrtomb()`.
- Conversion buffers are owned by `EditLine` scratch fields and reused; callers should not retain results after subsequent conversions using the same buffer.
- `ct_encode_string()` aborts if `ct_encode_char()` unexpectedly reports insufficient space after pre-growth.
