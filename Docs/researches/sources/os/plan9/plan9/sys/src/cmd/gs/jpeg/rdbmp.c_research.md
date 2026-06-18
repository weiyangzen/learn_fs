# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdbmp.c

This file implements BMP input support for IJG's `cjpeg` application when `BMP_SUPPORTED` is enabled. It reads Microsoft Windows and OS/2 BMP variants from a stdio stream and supplies RGB scanlines to the JPEG compressor source interface.

The private source object stores the public `cjpeg_source_struct`, a compressor back pointer, an optional BMP colormap, a virtual sample array containing the entire source image, row state, padded file row width, and bit depth.

`start_input_bmp()` parses the BMP file header and info header. It supports OS/2 1.x 12-byte headers and Windows/OS2 40/64-byte headers, accepts only 8-bit indexed and 24-bit RGB BMPs, rejects unsupported depths, bad planes, compressed BMPs, bad headers, and bad colormaps, and imports density from pixels-per-meter when available.

For indexed BMPs, `read_colormap()` reads either OS/2 BGR triples or Windows BGR0 quads and stores them in RGB component planes. The code assumes up to 256 palette entries.

BMP rows are bottom-up and padded to a 4-byte boundary, so `preload_image()` reads the entire image into a libjpeg virtual array in file order. Subsequent row callbacks decrement `source_row` to return scanlines top-to-bottom. `get_8bit_row()` expands palette indexes to RGB, and `get_24bit_row()` converts file BGR byte order to RGB.

`jinit_read_bmp()` allocates the source object and installs `start_input` and `finish_input`. Dependencies include `cdjpeg.h`, libjpeg memory managers, `JFREAD`, progress callbacks, and cjpeg source contracts.

Constraints: no 1-bit/4-bit BMP, no RLE compression, no top-down BMP handling is evident, and input is assumed to begin at the file start. This is image import code only.
