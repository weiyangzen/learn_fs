# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/yuv.c

Interactive viewer/converter command for Abekas-style YUV files. It calls `readyuv(fd, CYCbCr)` and then displays or writes converted output.

Its flag set and control flow match `tga.c`/`v210.c`: choose compressed or Plan 9 raw output, grayscale/RGBV/true-color conversion, suppress display, and toggle error diffusion. Display uses libdraw window setup and keyboard wait.

Decoded images are converted through `torgbv` or `totruecolor`, then freed with the source `Rawimage` array.
