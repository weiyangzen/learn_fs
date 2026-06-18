# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegint.h

Internal IJG declarations shared by JPEG library modules. Applications normally include only `jpeglib.h`.

It defines buffer-controller pass modes, compression/decompression global-state constants, and the public portions of internal module structs: compressor/decompressor masters, main/prep/post/coefficient controllers, color conversion, downsampling/upsampling, DCT/IDCT, entropy coding, marker reading/writing, and quantization.

The header declares module initialization entry points, utility routines from `jutils.c`, and natural-order coefficient tables. It also provides `MAX`, `MIN`, signed-right-shift portability macros, short external-name mappings for limited linkers, and dummy incomplete-type definitions for broken compilers.
