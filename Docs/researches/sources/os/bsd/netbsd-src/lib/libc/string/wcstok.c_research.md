# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcstok.c

Implements `wcstok()`, the reentrant wide-character tokenizer. It skips leading delimiters, identifies the next token, replaces a delimiter with wide NUL when needed, and stores continuation state in `*last`.

It mirrors `strtok_r()` logic for `wchar_t` strings.
