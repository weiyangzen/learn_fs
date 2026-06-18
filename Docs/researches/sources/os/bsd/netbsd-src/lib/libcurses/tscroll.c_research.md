# File Research: sources/os/bsd/netbsd-src/lib/libcurses/tscroll.c

This file formats terminal capability strings used for scrolling and cursor-control style sequences. It derives from termcap `tgoto`-style expansion and provides a small varargs formatter over `%` escapes.

Key entry points:
- `__tscroll(const char *cap, int n1, int n2)` forwards to `__parse_cap()`.
- `__parse_cap(char const *cap, ...)` expands termcap-style percent sequences into a static `MAXRETURNSIZE` result buffer.

Supported escape behavior:
- Numeric output: `%d`, `%2`, `%3`.
- Character output: `%.`, `%+x`.
- Value transformation: `%>xy`, `%i`, `%n`, `%B`, `%D`.
- Literal percent: `%%`.
- `%pN` is ignored as a limited System V terminfo compatibility concession.
- `%r` is documented as unsupported.

Important state and control flow:
- The parser lazily consumes one integer argument at a time into `n`, tracks whether a value is currently loaded with `have_input`, and clears that state after output-producing escapes.
- Errors, NULL capabilities, or unknown escapes return a static empty string.
- The output buffer is static, so callers must treat it as overwritten by later calls and not thread-safe.

Risks and notes:
- There is no explicit bounds checking on the static result buffer while appending output.
- Only a subset of terminfo expansion syntax is supported.
- Debug tracing uses `unctrl()` to display nonprinting capability bytes.
