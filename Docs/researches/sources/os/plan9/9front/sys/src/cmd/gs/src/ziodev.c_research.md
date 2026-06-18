# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev.c

## Purpose
Implements standard IODevice support and the `%lineedit%` / `%statementedit%` line-buffering helper.

## Key Functions
- `zgetiodevice()` returns IODevice names by numeric index.
- `zfilelineedit()` reads from stdin, builds an editable line or statement string, and returns a string-backed file stream.

## Important Behavior
- `%lineedit%` and `%statementedit%` are declared as special devices but actual opening is handled by interpreter code.
- `zfilelineedit()` grows a PostScript string buffer up to `max_string_size`.
- Statement mode scans tokens and continues reading until a complete statement is present.
- Handles stdin callouts via `s_handle_read_exception()`.
- Returned streams read from the completed line buffer and disable normal close freeing.

## Research Notes
This is interpreter-side IODevice/file-stream glue, relevant to file abstractions but not Plan 9 VFS internals.
