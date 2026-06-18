# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpeglib.h

Public IJG JPEG library API header for version 6b (`JPEG_LIB_VERSION 62`). It includes `jconfig.h` and `jmorecfg.h`, defines JPEG standard limits, and establishes application-visible data types.

The header defines sample and coefficient array types, quantization and Huffman table structs, component metadata, scan scripts, saved marker lists, color-space enums, DCT method enums, and dithering modes. It defines the common, compression, and decompression master structs, including public parameters, computed state, marker metadata, progress counters, and links to internal submodules.

It also declares the standard error manager, progress manager, source/destination managers, and memory manager interfaces. Exported API prototypes cover object creation/destruction, stdio source/destination setup, compression parameter setup, scanline/raw-data compression and decompression, buffered-image mode, marker saving/processing, coefficient-level transcoding, abort/destroy helpers, restart resynchronization, and marker constants. When `JPEG_INTERNALS` is defined, it includes `jpegint.h` and `jerror.h`.
