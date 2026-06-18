# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/header.c

This file handles RFC 822 header length detection and RFC 2047 encoded-word decoding.

Key behavior:
- `hdrlen` returns a complete folded header line length, including continuation lines.
- `tokbegin` finds the start of an encoded word ending at a candidate position.
- `tok` decodes `=?charset?b?...?=` and `=?charset?q?...?=` tokens, converts through `xtoutf`, and appends to output.
- `rfc2047` scans a header line, decodes encoded words, optionally folds continuation whitespace, strips control chars as appropriate, and NUL-terminates output.
- Supports both base64 and quoted-printable encoded-word payloads.

Integration and risks:
- Used by `fs.c` when serving headers and by `mbox.c` while parsing headers.
- Output buffers are caller-provided; too-small encoded token conversion falls back to literal copying.
