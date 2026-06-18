# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2eps.c

This file translates JPEG image data into EPS/PostScript output.

Key routine:
- `bTranslateJPEG(...)` seeks to the embedded JPEG data, emits an image prologue, ASCII85-encodes the JPEG bytes into the output file, then emits an image epilogue.

Debug behavior:
- Under `DEBUG`, `vCopy2File(...)` can dump the embedded JPEG to `/tmp/pic/picNNNN.jpg`.

Dependencies:
- Data offset seeking, image prologue/epilogue emission, ASCII85 file encoder, diagram output file state.

Role in antiword:
- Provides the non-RISC OS PostScript/PDF-style JPEG embedding path.
