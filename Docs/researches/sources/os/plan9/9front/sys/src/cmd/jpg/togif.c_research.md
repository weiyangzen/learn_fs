# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/togif.c

Command-line converter from Plan 9 image input to GIF. It reads `Memimage` data from stdin or files, converts to one-channel palette form with `memonechan`, and writes through `memstartgif`, `memwritegif`, and `memendgif`.

Options support loop count, comment, per-frame delay in milliseconds, transparency index, and `-E` streaming multiple images from stdin until EOF. For multiple file arguments, inline `-d` arguments can change subsequent frame delay.

The command manages animation defaults: no loop for a single image, infinite loop for multiple files unless explicitly overridden.
