# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib.h

IJG v6b public application interface header for the JPEG library. It includes `jconfig.h` unless `JCONFIG_INCLUDED` was already set by `jinclude.h`, then includes `jmorecfg.h`. In this repository, `jpeglib.h`, `jpeglib0.h`, and `jpeglib_.h` are byte-identical.

The header declares JPEG standard constants and table limits, including `JPEG_LIB_VERSION 62`, `DCTSIZE`, quantization/Huffman table counts, arithmetic table count, scan component limits, sampling factor limits, `C_MAX_BLOCKS_IN_MCU`, and `D_MAX_BLOCKS_IN_MCU` with an override path from `jmorecfg.h`.

It defines public sample/coefficient array types:
- `JSAMPROW`, `JSAMPARRAY`, and `JSAMPIMAGE` for image samples.
- `JBLOCK`, `JBLOCKROW`, `JBLOCKARRAY`, and `JBLOCKIMAGE` for DCT coefficient blocks.
- `JCOEFPTR` for coefficient pointers.

It defines public JPEG data structures:
- `JQUANT_TBL` and `JHUFF_TBL` for quantization and Huffman tables.
- `jpeg_component_info` for per-component sampling, table selectors, computed dimensions, MCU layout, quantization table pointer, and DCT private storage.
- `jpeg_scan_info` for multiscanner/progressive scan scripts.
- `jpeg_marker_struct` and `jpeg_saved_marker_ptr` for saved APPn/COM markers.
- `J_COLOR_SPACE`, `J_DCT_METHOD`, and `J_DITHER_MODE` enums.

The main state records are `jpeg_common_struct`, `jpeg_compress_struct`, and `jpeg_decompress_struct`. `jpeg_common_fields` must remain prefix-identical across common, compressor, and decompressor records. The compressor struct contains destination manager, source image description, compression parameters, tables, scan script, restart settings, marker settings, progress state, computed MCU state, and module pointers. The decompressor struct contains source manager, image metadata, output parameters, quantization options, output dimensions, output progress, progressive status, tables, marker metadata, computed MCU state, unread marker state, and module pointers.

It declares application-visible module objects:
- `jpeg_error_mgr` for fatal error exit, warnings/tracing, formatting, reset, message tables, and warning counts.
- `jpeg_progress_mgr` for progress callback state.
- `jpeg_destination_mgr` and `jpeg_source_mgr` for buffered output/input callbacks.
- `jpeg_memory_mgr` for pooled allocation, virtual sample/block arrays, pool freeing, object destruction, memory limits, and allocation chunk limits.

The public API prototypes cover:
- Error setup: `jpeg_std_error`.
- Object creation/destruction: `jpeg_create_compress`, `jpeg_create_decompress`, `jpeg_CreateCompress`, `jpeg_CreateDecompress`, `jpeg_destroy_compress`, `jpeg_destroy_decompress`.
- Stdio source/destination managers.
- Compression parameter setup: defaults, colorspace, quality scaling, quantization table setup, progression, table suppression, table allocation.
- Compression execution: start, write scanlines/raw data, finish, marker writing, table-only output.
- Decompression execution: read header, start/read/finish scanlines, raw data, buffered-image mode, input consumption, output-dimension calculation.
- Marker save/processor hooks.
- Coefficient read/write and critical-parameter copying for transcoding.
- Abort/destroy common helpers and restart-marker resynchronization.

It exports JPEG marker codes `JPEG_RST0`, `JPEG_EOI`, `JPEG_APP0`, and `JPEG_COM`, result constants for header/input processing, optional short external-name remaps for limited linkers, and dummy incomplete-type definitions when `INCOMPLETE_TYPES_BROKEN` is set. If `JPEG_INTERNALS` is defined, it also includes `jpegint.h` and `jerror.h`.

Filesystem relevance: indirect. The API can read/write JPEG streams through `FILE *` managers, but this file is an image-codec API header for Ghostscript, not an OS/filesystem component.
