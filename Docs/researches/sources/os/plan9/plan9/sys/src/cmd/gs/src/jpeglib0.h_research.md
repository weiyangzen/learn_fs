# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib0.h

## Identity

- Lines/bytes: 1,096 lines, 46,205 bytes.
- SHA-256: `b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
- Role: private-build copy of IJG v6b `jpeglib.h`.
- Duplicate note: byte-identical to `jpeglib.h` and `jpeglib_.h`.

## Contents And API

This file contains the same public IJG JPEG API as `jpeglib.h`:

- JPEG v6b version and standard constants.
- Image sample and coefficient array types.
- Quantization/Huffman/component/scan/marker structures.
- Compression and decompression master structs.
- Error, progress, source, destination, and memory manager interfaces.
- Compression, decompression, marker, coefficient, abort, destroy, and restart-resync function declarations.

## Build Role

According to `jpeg.mak`, `jpeglib0.h` is produced from the IJG source `jpeglib.h` for `SHARE_JPEG=0`, when Ghostscript builds its private JPEG library. It is then selected into `jpeglib_.h` depending on the share/private mode.

## Dependencies

- Includes `jconfig.h` unless already included.
- Includes `jmorecfg.h`.
- May include private `jpegint.h` and `jerror.h` under `JPEG_INTERNALS`.

## Research Notes

- No semantic differences from `jpeglib.h` were found.
- The `0` suffix is a build-mode convention: private/bundled JPEG rather than shared-system JPEG.
