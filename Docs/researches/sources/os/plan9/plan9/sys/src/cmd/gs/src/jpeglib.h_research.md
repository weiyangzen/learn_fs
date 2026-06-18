# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib.h

## Identity

- Lines/bytes: 1,096 lines, 46,205 bytes.
- SHA-256: `b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
- Role: IJG v6b public JPEG library API header.
- Duplicate note: byte-identical to `jpeglib0.h` and `jpeglib_.h`.

## Public API Surface

The header defines:

- Version: `JPEG_LIB_VERSION 62`.
- JPEG constants: DCT block size, table counts, scan component limits, sampling limits, compressor/decompressor MCU block limits.
- Core image/coefficient array pointer types: `JSAMPROW`, `JSAMPARRAY`, `JSAMPIMAGE`, `JBLOCK`, `JBLOCKROW`, `JBLOCKARRAY`, `JBLOCKIMAGE`, `JCOEFPTR`.
- Quantization and Huffman table structs: `JQUANT_TBL`, `JHUFF_TBL`.
- Component metadata: `jpeg_component_info`.
- Progressive/multiscan script entries: `jpeg_scan_info`.
- Saved marker list nodes: `jpeg_marker_struct`.
- Color spaces, DCT methods, and dithering modes.

## Master Structures

Defines the common, compression, and decompression objects:

- `jpeg_common_struct`: shared error, memory, progress, client data, object kind, and state fields.
- `jpeg_compress_struct`: destination manager, source image description, compression parameters, quant/Huffman tables, scan script, marker flags, progress state, computed MCU state, and compressor subobject pointers.
- `jpeg_decompress_struct`: source manager, input image description, decompression parameters, output dimensions, quantization/color map state, progress state, saved marker metadata, computed MCU state, unread marker, and decompressor subobject pointers.

## Managers And Callbacks

Defines public “object” interfaces for:

- `jpeg_error_mgr`.
- `jpeg_progress_mgr`.
- `jpeg_destination_mgr`.
- `jpeg_source_mgr`.
- `jpeg_memory_mgr`.
- `jpeg_marker_parser_method`.

The memory manager uses permanent and image pools and supports virtual sample/block arrays.

## Exported Functions

Compression lifecycle and configuration:

- `jpeg_create_compress`, `jpeg_CreateCompress`, `jpeg_destroy_compress`.
- `jpeg_stdio_dest`.
- `jpeg_set_defaults`, `jpeg_set_colorspace`, `jpeg_default_colorspace`.
- `jpeg_set_quality`, `jpeg_set_linear_quality`, `jpeg_add_quant_table`, `jpeg_quality_scaling`.
- `jpeg_simple_progression`, `jpeg_suppress_tables`.
- `jpeg_start_compress`, `jpeg_write_scanlines`, `jpeg_write_raw_data`, `jpeg_finish_compress`.
- Marker and table writing APIs.

Decompression lifecycle and processing:

- `jpeg_create_decompress`, `jpeg_CreateDecompress`, `jpeg_destroy_decompress`.
- `jpeg_stdio_src`.
- `jpeg_read_header`, `jpeg_start_decompress`, `jpeg_read_scanlines`, `jpeg_read_raw_data`, `jpeg_finish_decompress`.
- Buffered-image/progressive APIs.
- Marker saving/processing APIs.
- Raw coefficient read/write/copy APIs.

Generic cleanup:

- `jpeg_abort_compress`, `jpeg_abort_decompress`, `jpeg_abort`, `jpeg_destroy`.
- `jpeg_resync_to_restart`.

## Dependencies

- Includes `jconfig.h` unless `JCONFIG_INCLUDED` is already set.
- Includes `jmorecfg.h`.
- References `FILE`, so users normally get this through `jinclude.h` or include standard I/O context.
- Includes `jpegint.h` and `jerror.h` only when `JPEG_INTERNALS` is defined.

## Research Notes

- Ghostscript’s `jmorecfg.h` can raise `D_MAX_BLOCKS_IN_MCU` before this header defines the decompressor default.
- The public ABI depends on configuration types from `jmorecfg.h`.
- This is third-party JPEG library API surface embedded in the Plan 9 Ghostscript source tree.
