# File Research: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regsub.c

Read completely: 87 lines.

Implements `__compat_regsub()`, the replacement/substitution helper for Henry Spencer regexp matches. It validates non-null inputs and the compiled regexp magic byte, then copies a replacement template into the caller-provided destination buffer.

Substitution syntax is legacy and minimal: `&` expands to the whole match, `\0` through `\9` expand to captured subexpressions, and escaped `\\` or `\&` emit literal backslash/ampersand. Match text comes from `prog->startp[]` and `prog->endp[]`, which are populated by `__compat_regexec()`.

The destination has no explicit length argument, so callers must provide enough space. It uses `strncpy()` for captured substrings and checks whether a copied NUL implies a damaged match string.
