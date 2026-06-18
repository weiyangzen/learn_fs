# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev.c

Standard IODevice support and line-edit/statement-edit stream construction. It defines `%lineedit%` and `%statementedit%` device descriptors as special devices and registers `.getiodevice`.

`zgetiodevice` maps an integer IODevice index to its device name string or `null`, returning range errors for invalid indexes. The larger `zfilelineedit` routine is the implementation/continuation for `.filelineedit`: it reads from `%stdin` into a PostScript string buffer, grows the buffer up to `max_string_size`, handles read callouts, EOF, and I/O errors, and returns a string-backed file stream.

For statement editing, it appends an EOL and scans the accumulated buffer to decide whether a complete token/statement has been read; if the scanner needs refill, reading continues. The final stream disables close freeing of the backing string buffer and sets its filename to `%lineedit%` or `%statementedit%`. This file is interpreter-facing terminal input handling rather than OS filesystem logic.
