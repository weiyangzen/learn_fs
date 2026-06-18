# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/conv.c

Main parser for troff device-independent output in `tr2post`. It reads command bytes from a `Biobufhdr` and dispatches to font, motion, drawing, device-control, page, and glyph output handlers.

Key behavior:
- Handles `s`, `f`, `c`, `C`, `H`, `V`, `h`, `v`, two-digit motion-plus-character forms, `p`, `n`, `w`, `D`, `x`, comments, and newlines.
- Calls `endpage()` before `startpage()` on `p`.
- Ignores numeric character command `N` after reading its value; no output path is implemented there.

Integration points:
- Central driver used by `tr2post.c` for stdin and each input file.
- Depends on motion/glyph/device/draw functions declared in `tr2post.h`.

Risks:
- `N` command is parsed but not emitted.
- Unknown troff functions only warn, which can hide unsupported input.
