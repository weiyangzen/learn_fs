# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.c

Common PostScript/PDF output syntax utilities and parameter-printing support.

Key behavior:
- `s_write_ps_string` writes bytes as either a literal PostScript string or hex string, choosing the shorter permitted form unless binary or hex restrictions force a choice.
- Binary string mode escapes only `(`, `)`, backslash, CR, and LF.
- Non-binary mode estimates literal-string escape overhead and uses `PSStringEncode` or `ASCIIHexEncode`.
- `s_alloc_position_stream` creates a write stream that tracks position only.
- Parameter-printer setup creates a `gs_param_list` implementation that writes non-default parameter key/value pairs to a stream.
- `param_print_typed` prints null, bool, int, long, float, string, name, int array, and float array values in PostScript/PDF-like syntax.

Notable dependencies:
- Printing helpers from `spprint.h`.
- String/hex filters from `sstring.h`, `sa85x.h`.
- Ghostscript parameter list APIs from `gsparam.h`.

Research notes:
- ASCII85 string output is noted but not implemented.
- Name printing has a comment that PDF `#` escaping should be used but is not.
- In `param_print_typed`, the long case uses format `" %l"` even though `pprintld1` debug-checks for `%ld`; this looks suspicious in debug builds and may omit the expected `d`.
