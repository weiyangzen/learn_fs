# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2sprt.c

RISC OS Draw/sprite-side JPEG translator.

Key functions:

- `bSave2Draw()` reads the JPEG payload into memory and embeds it in a Draw diagram via `vImage2Diagram()`.
- `bTranslateJPEG()` seeks to JPEG data and, on RISC OS 3.6 or later, saves the JPEG into the Draw file; older systems fall back to a dummy image.

Debug-only code can dump JPEGs to the RISC OS scrap directory, but it is disabled with `#if 0`.

Unlike `jpeg2eps.c`, this path embeds the raw JPEG in a Draw diagram rather than ASCII85-encoding it.
