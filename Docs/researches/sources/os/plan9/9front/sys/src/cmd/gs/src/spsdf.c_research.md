# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spsdf.c

Implements common PostScript/PDF syntax output utilities.

Key points:
- `s_write_ps_string` writes byte strings in efficient PostScript syntax, choosing literal string form or hex string form depending on binary permission and escaping cost.
- Literal binary-allowed mode only escapes parentheses, backslash, CR, and EOL.
- Non-binary mode uses `PSStringEncode` or `ASCIIHexEncode` stream templates to generate escaped text.
- `s_alloc_position_stream` allocates a write stream that only tracks byte position.
- Defines a `printer_param_list_t` implementation of Ghostscript parameter-list transmission that prints parameters as PostScript-style `/Key value` syntax.
- Parameter printer handles null, bool, int, long, float, string, name, int array, and float array values; unsupported arrays return typecheck.
- Release/free paths emit suffixes only if at least one parameter was printed.

Dependencies and interactions:
- Uses `spprint.h`, `sstring.h`, `sa85x.h`, `gsparam.h`, and stream APIs.

Research relevance:
- Utility layer for serializing strings and filter parameter dictionaries in PostScript/PDF output.
