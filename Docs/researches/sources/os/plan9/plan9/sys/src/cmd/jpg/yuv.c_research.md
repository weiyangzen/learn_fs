# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/yuv.c

This is the `yuv` image viewer/converter command. It reads YUV/YCbCr raw images through `readyuv(fd, CYCbCr)`, optionally displays them using libdraw/event, and optionally writes Plan 9 bitmap/rawimage output.

Command flags control output and display: `-3`, `-t`, `-c`, `-d`, `-e`, `-k`, `-v`, and `-9`. They select compressed/raw output, suppress display, disable Floyd-Steinberg diffusion, force grayscale, force RGBV/CMAP8, or output uncompressed Plan 9 bitmap data.

`show()` performs decode, colorspace conversion through `torgbv()` or `totruecolor()`, display allocation/loading, keyboard wait/quit handling, and output serialization through either a Plan 9 bitmap header plus channel bytes or `writerawimage()`.

Filesystem and OS interactions are simple file reads and stdout writes, plus graphical window attachment. Resource cleanup frees decoded raw image channels, colormap, raw image structures, and converted output buffers, though early error paths can bypass some cleanup.
