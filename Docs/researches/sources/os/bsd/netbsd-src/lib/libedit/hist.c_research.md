# File Research: sources/os/bsd/netbsd-src/lib/libedit/hist.c

This file connects `EditLine` to a history backend.

Key functions:
- `hist_init()` allocates the current-line history scratch buffer.
- `hist_end()` frees it.
- `hist_set()` installs the history function pointer and reference pointer.
- `hist_get()` loads either the saved current line or a selected history event into `el_line`.
- `hist_command()` implements editline `history` subcommands.
- `hist_enlargebuf()` grows the internal history scratch buffer.
- `hist_convert()` adapts narrow-history responses to wide strings.

Important behavior:
- `hist_get()` treats `eventno == 0` as the current editable line and restores from `el_history.buf`.
- For nonzero history events, it starts at `HIST_FIRST()` and walks forward `eventno - 1` entries.
- Loaded history lines have trailing newline and trailing space trimmed.
- Cursor placement differs for vi vs non-vi maps.
- `hist_command()` supports listing history and setting `size` or `unique`.

Integration:
- Uses macros from `hist.h` to call the installed history backend.
- Uses `ct_encode_string()`, `ct_decode_string()`, and `strvis()` for display/conversion.

Risks and notes:
- If no history backend is installed, history operations return errors.
- History listing dynamically grows a temporary escaped-output buffer.
- `hist_convert()` relies on `NARROW_HISTORY` callers passing narrow strings through a wide-event typed interface.
