## sources/user-network-fs/samba/source3/lib/srprs.c

Purpose: implementation of a small recursive-descent parsing helper library. It advances a `const char **` parse cursor only on success and appends matched text to an optional `cbuf`, which makes it useful for simple line, quoted-string, charset, and hex parsers.

Important functions mirror the header: `srprs_skipws`, `srprs_char`, `srprs_str`, `srprs_charset`, `srprs_charsetinv`, `srprs_quoted_string`, `srprs_hex`, `srprs_nl`, `srprs_eos`, `srprs_eol`, `srprs_line`, and `srprs_quoted`. `srprs_quoted_string` supports continuation across invocations through a `bool *cont`; `srprs_quoted` supports `\"`, `\\`, and two-digit hex escapes.

Control flow is intentionally simple. Matchers snapshot the incoming cursor and, for buffer-writing functions, the `cbuf` position. On failure they leave the cursor unchanged and restore the buffer position. `srprs_str` calculates the remaining null-terminated input length before `memcmp` to avoid reading past the buffer. Newline parsing recognizes CRLF first, then single LF or CR.

State and persistence: no global or durable state exists. All parse state is caller-owned via the input pointer and `cbuf`. Dependencies are `replace.h`, locale character classification, `cbuf`, and assertions.

Risks: all input is assumed null-terminated. `srprs_skipws` passes `char` values to `isspace` without unsigned-char casting, which can be undefined for negative bytes under some locales. `srprs_hex` accepts fewer than the requested number of hex digits as long as `sscanf` parses something, despite the `len` wording. Test signals should focus on cursor rollback, cbuf rollback, CR/LF variants, continuation strings, invalid escapes, and high-bit input.
