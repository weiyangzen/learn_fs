# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scanchar.h

Defines the scanner character classification interface for Ghostscript token scanning. It declares `scan_char_array`, defines `scan_char_decoder` with an exception offset, and assigns classification constants for digits, names, binary tokens, whitespace, exceptions, and other characters.

It also defines scanner-level special characters such as NULL, EOT, vertical tab, DOS EOF, CR, and abstract EOL handling for platforms where newline and carriage return differ unusually.

Dependencies include `scommon.h` for stream exception counts. The table implementation is in `scantab.c`.

This is PostScript/PDF tokenization support, not filesystem logic.
