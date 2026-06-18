# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writepng.c

PNG writer for `Memimage`. It writes PNG signature, IHDR, tIME, optional gAMA, optional tEXt comment, compressed IDAT chunks, and IEND.

`memRGBA` converts source images to BGR24 or ABGR32 arranged so the byte stream becomes PNG RGB/RGBA order. Alpha channels are converted from Plan 9 premultiplied representation back to non-premultiplied PNG samples during zlib input streaming.

The writer uses filter type None only, no interlace, 8 bits per channel, and zlib compression level 6.
