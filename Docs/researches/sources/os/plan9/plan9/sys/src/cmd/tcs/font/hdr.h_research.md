# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/hdr.h

Shared declarations for the `tcs/font` tools.

Defines:
- `readbitsfn`: reader function type returning `Bitmap *`.
- `mapfn`: mapping function type from rune range to glyph ordinals.

Declares:
- Reader/mapping pairs for Kuten/JIS, Big5, GB BDF, and quwei GB sources.
- `bf` for constructing a `Subfont`.

Role:
- Shared by `main.c`, bit readers, and map modules.
