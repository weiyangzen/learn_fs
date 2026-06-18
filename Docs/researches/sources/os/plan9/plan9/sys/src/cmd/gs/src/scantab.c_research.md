# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scantab.c

Definition of the scanner character-class table declared by `scanchar.h`.

The table maps stream exceptions and all 256 byte values to Ghostscript scanner categories:

- Whitespace for NUL, tab, LF, FF, CR, and space.
- `ctype_other` for token delimiters such as `%`, parentheses, slash, angle brackets, brackets, and braces.
- Numeric digit values for `0-9`, `A-Z`, and `a-z` where applicable.
- `ctype_btoken` for bytes 128-159.
- `ctype_name` for most remaining bytes, including high bytes 160-255.

This table is used for fast token scanning in PostScript/PDF parsing. It is not filesystem code.
