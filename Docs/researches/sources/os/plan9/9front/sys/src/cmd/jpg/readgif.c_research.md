# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readgif.c

GIF87a/GIF89a decoder returning an array of `Rawimage*`. `readgif` accepts `justone`, initializes a `Header` state object, and uses `setjmp`/`longjmp` cleanup paths for parse and allocation failures.

The parser reads global/local color maps, image descriptors, graphic-control extensions, comments/application extensions, NETSCAPE loop counts, LZW image data, and GIF interlacing. Decoded frames carry GIF metadata fields such as delay, transparency index, flags, and loop count.

The LZW decoder keeps reading through malformed overflow cases to preserve stream synchronization. `colorspace` is unused; decoded frames are indexed `CRGB1` with a copied color map.
