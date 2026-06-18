# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jpeglib.h

Purpose: public IJG JPEG library API header for version 6b.

Key public definitions:
- `JPEG_LIB_VERSION 62`.
- JPEG standard limits.
- Application-visible data types.
- Sample and coefficient array types.
- Quantization and Huffman table structs.
- Component metadata.
- Scan scripts.
- Saved marker lists.
- Color-space enums.
- DCT method enums.
- Dithering modes.

Major structs:
- `jpeg_common_struct`
- `jpeg_compress_struct`
- `jpeg_decompress_struct`
- `jpeg_error_mgr`
- `jpeg_progress_mgr`
- `jpeg_destination_mgr`
- `jpeg_source_mgr`
- `jpeg_memory_mgr`

Exported APIs:
- Object creation/destruction.
- Standard error-manager setup.
- stdio source/destination setup.
- Compression parameter setup.
- Scanline and raw-data compression/decompression.
- Buffered-image decompression mode.
- Marker saving and custom marker processing.
- Coefficient-level transcoding.
- Abort/destroy helpers.
- Restart-marker resynchronization.
- Public JPEG marker constants.

Important behavior:
- `jpeg_create_compress()` and `jpeg_create_decompress()` macro-wrap version and structure-size checks.
- Memory management is exposed as pool-based allocation plus virtual-array support.
- When `JPEG_INTERNALS` is defined, this header includes `jpegint.h` and `jerror.h`.

Notes:
- This is the main API surface used by applications and by the internal JPEG modules.
