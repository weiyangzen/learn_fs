# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/sub.c

Small utility module for `webfs` memory allocation, bounded string copying, HTTP header key lists, header parsing, and quoted-token parsing.

Key behavior:
- `emalloc()` and `estrdup()` wrap lib9p allocation helpers, set malloc tags, and zero allocated blocks.
- `nstrcpy()` copies with guaranteed NUL termination.
- `addkey()`, `delkey()`, `getkey()`, and `lookkey()` manage case-insensitive linked header lists.
- `parsehdr()` trims trailing whitespace, splits `Key: value` lines, strips leading value whitespace, and returns a `Key`.
- `unquote()` parses either quoted strings with backslash skipping or whitespace-delimited tokens, mutating the buffer and returning the unquoted token.

Notable dependencies:
- Plan 9 ctype/case-insensitive string helpers and lib9p allocation.

Research notes:
- Deleting a header zeroes its value before freeing.
- Parsing helpers are destructive by design.
