# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.h

Header for `cb`’s private ASCII ctype implementation. It defines classification bit masks and declares `_cbtype_[]`.

Macros classify operators, alphabetics, digits, whitespace, punctuation, printable/control ASCII, and hex digits by indexing `_cbtype_ + 1`. It also defines simple ASCII-only `toupper`, `tolower`, and `toascii`.
