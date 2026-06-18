# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib_.h

Selected/wrapper-name copy of the IJG v6b public application interface header. It is byte-identical to `jpeglib.h` and `jpeglib0.h` in this snapshot. The underscore name is part of Ghostscript's generated-header convention: `jpeg.mak` builds `jpeglib_.h` from either the local vendored header path or a shared-system JPEG include wrapper depending on `SHARE_JPEG`.

Because the content is the full local IJG public header here, it defines the complete libjpeg v6b API surface: configuration includes, version and JPEG constants, public sample/coefficient/table types, component/scan/marker structures, compressor and decompressor state records, manager callback structs, public entry points for compression, decompression, marker handling, raw coefficient I/O, lifecycle cleanup, and restart resynchronization.

The header is sensitive to Ghostscript-generated configuration:
- `jconfig.h` supplies portability and type feature macros.
- `jmorecfg.h` supplies datatype definitions and trims optional JPEG features.
- `JPEG_INTERNALS` switches the tail of the header from application-only declarations to include `jpegint.h` and `jerror.h` for JPEG library implementation files.

Filesystem relevance: indirect. It declares stdio-based source/destination setup functions but otherwise belongs to Ghostscript's embedded JPEG codec integration.
