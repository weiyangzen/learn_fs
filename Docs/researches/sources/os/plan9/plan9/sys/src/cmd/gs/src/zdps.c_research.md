# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps.c

Implements Display PostScript extensions.

Graphics-state screen phase operators:
- `.setscreenphase`
- `.currentscreenphase`

`.image2` implements device-source image drawing from a dictionary. It reads `ImageMatrix`, `DataSource`, `XOrigin`, `YOrigin`, `Width`, `Height`, `PixelCopy`, and optional `UnpaintedPath`. If `UnpaintedPath` is requested, it allocates a path, processes the image, converts the resulting path to a user path, and writes it back into the dictionary.

View clipping operators:
- `viewclip`
- `eoviewclip`
- `initviewclip`
- `viewclippath`

`defineusername` maintains the global user-name array used by binary token support. It expands the array in stable local VM, preserves entries across save/restore, and rejects conflicting redefinition.

Registered in `zdps_op_defs`.
