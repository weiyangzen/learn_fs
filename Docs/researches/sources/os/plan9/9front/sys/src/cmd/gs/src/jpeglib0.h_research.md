# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib0.h

Local-build copy of the IJG v6b public application interface header. It is byte-identical to `jpeglib.h` and `jpeglib_.h` in this source tree. `jpeg.mak` uses this naming convention to distinguish the local vendored JPEG API (`0`) from a shared-system JPEG wrapper (`1`) before copying/selecting the final generated include target.

Semantically, this file exposes the same API as `jpeglib.h`: JPEG library version `62`, JPEG constants, sample and coefficient array types, quantization/Huffman tables, component and scan descriptors, saved marker structures, colorspace/DCT/dither enums, compressor/decompressor master structs, error/progress/source/destination/memory manager objects, public compression/decompression/transcoding functions, marker constants, and optional internal includes under `JPEG_INTERNALS`.

Important integration details:
- Includes `jconfig.h` and `jmorecfg.h`, so Ghostscript's generated configuration and wrapper feature choices control the public types and enabled code paths.
- `D_MAX_BLOCKS_IN_MCU` can be overridden by Ghostscript's `jmorecfg.h`, where this tree sets it to `64` for Adobe-compatible decoding.
- Stdio source/destination manager prototypes expose `FILE *`, tying this API to C stdio when those helpers are used.

Filesystem relevance: indirect only through stdio stream managers. The file is codec API surface, not filesystem code.
