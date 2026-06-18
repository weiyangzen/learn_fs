# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/tga.c

Interactive TGA viewer/converter command. It reads TGA via `readtga`, optionally displays it in a draw window, and can emit Plan 9 raw image formats.

Command flags select display suppression, Floyd-Steinberg diffusion, grayscale/RGBV/true-color output, compressed raw output through `writerawimage`, or uncompressed Plan 9 image output. The display path centers the image and waits for keyboard input before continuing.

Conversion routes through `torgbv` for `CMAP8` output or `totruecolor` for gray/RGB/RGBA output.
