# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/chan.c

Converts between Plan 9 draw channel descriptors and textual channel strings.

Key functions:
- `chantostr`: validates a descriptor with `chantodepth`, reverses descriptor byte order, and emits strings like `r8g8b8`.
- `strtochan`: parses channel strings into packed descriptors using channel names `rgbkamx`.
- `chantodepth`: validates per-channel bit counts and aggregate depth rules, then returns total depth.

Important behavior:
- Avoids `ctype` by using a local whitespace helper.
- Rejects invalid channel types, bit counts greater than 8, zero-bit channels, and aggregate depths that do not align to Plan 9 image rules.
