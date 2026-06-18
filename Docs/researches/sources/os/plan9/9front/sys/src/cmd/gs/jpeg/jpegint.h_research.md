# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jpegint.h

Purpose: internal IJG declarations shared by JPEG library modules.

Key contents:
- Buffer-controller pass modes.
- Compression and decompression global-state constants.
- Public portions of internal module structs:
  - compressor/decompressor masters
  - main/prep/post/coefficient controllers
  - color conversion/deconversion
  - downsampling/upsampling
  - DCT/IDCT
  - entropy coding
  - marker reading/writing
  - quantization
- Module initialization declarations.
- Utility routines from `jutils.c`.
- Natural-order coefficient tables.
- `MAX` and `MIN` helpers.
- Signed-right-shift portability macros.
- Short external-name mappings for limited linkers.
- Dummy incomplete-type definitions for broken compilers.

Important behavior:
- Applications normally include only `jpeglib.h`; this header is pulled in when `JPEG_INTERNALS` is defined.
