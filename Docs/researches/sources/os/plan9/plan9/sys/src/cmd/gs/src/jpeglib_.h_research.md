# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib_.h

## Identity

- Lines/bytes: 1,096 lines, 46,205 bytes.
- SHA-256: `b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
- Role: selected Ghostscript wrapper/copy for the active JPEG API header.
- Duplicate note: byte-identical to `jpeglib.h` and `jpeglib0.h`.

## Contents And API

This file exposes the IJG v6b application API:

- Public constants and JPEG data structures.
- Compression and decompression state objects.
- Manager callback structs for error handling, progress, memory, I/O source, and I/O destination.
- Public functions for JPEG object creation/destruction, compression, decompression, marker handling, coefficient access, buffered-image mode, and cleanup.

## Build Role

`jpeg.mak` builds `jpeglib_.h` by copying either:

- `jpeglib0.h` for bundled/private JPEG builds.
- `jpeglib1.h` for shared-system JPEG builds.

In this checked-in tree, the file content matches the private IJG header.

## Dependencies

- Includes `jconfig.h` and `jmorecfg.h`.
- Uses configuration-controlled type definitions from `jmorecfg.h`.
- Includes internal declarations only under `JPEG_INTERNALS`.

## Research Notes

- This is the stable include target Ghostscript can depend on while switching JPEG build modes.
- The checked-in copy represents the bundled IJG API path and contains no Plan 9 filesystem logic.
