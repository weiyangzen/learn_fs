# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scanchar.h

Header defining Ghostscript token-scanner character classification.

It declares `scan_char_array`, biased by `max_stream_exception`, and `scan_char_decoder`, which maps byte values and stream exceptions to scanner categories.

Categories include:

- Numeric digit values `0` through `max_radix - 1`.
- `ctype_name`.
- `ctype_btoken`.
- `ctype_space`.
- `ctype_other`.
- `ctype_exception`.

It also defines special control character constants such as `char_NULL`, `char_EOT`, `char_VT`, `char_DOS_EOF`, and portable `char_CR`/`char_EOL` handling for OS-9 newline peculiarities.

This supports PostScript/PDF lexical scanning, not filesystem behavior.
