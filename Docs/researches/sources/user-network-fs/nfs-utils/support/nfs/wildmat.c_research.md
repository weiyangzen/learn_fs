# sources/user-network-fs/nfs-utils/support/nfs/wildmat.c

Purpose: case-insensitive shell-style wildcard matcher supporting `*`, `?`, backslash literals, and bracket character classes.

Important API: `int wildmat(char *text, char *p)`. Internal `DoMatch()` returns true, false, or abort to optimize failing `*` patterns.

Control flow: walks pattern and text; `*` collapses consecutive stars and recursively tests suffixes; `?` matches any character; `[...]` supports ranges and `^` negation; default and escaped characters compare with `toupper()`. A pattern exactly equal to `*` returns true immediately.

State and persistence: no state.

Dependencies and integration: used for export/client matching patterns in NFS utilities via `nfslib.h`.

Risks: file comment warns malformed patterns such as incomplete ranges may not be robust. `toupper()` should be passed unsigned-char-compatible values; current code passes `char` values directly. Matching is case-insensitive, which may not fit all callers.

Test signals: literal, `*`, `?`, escaped metacharacters, classes/ranges/negation, malformed classes, empty strings, 8-bit input, and pathological star patterns.
