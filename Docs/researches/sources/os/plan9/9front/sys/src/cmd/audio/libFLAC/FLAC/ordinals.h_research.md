# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/ordinals.h

Public libFLAC fixed-width ordinal type header.

Important contents:
- Provides FLAC-specific integer typedefs: `FLAC__int8`, `FLAC__uint8`, `FLAC__int16`, `FLAC__uint16`, `FLAC__int32`, `FLAC__uint32`, `FLAC__int64`, and `FLAC__uint64`.
- Uses Microsoft-specific integer types for MSVC versions older than 2010, which lacked C99 `stdint.h`.
- Uses `<stdint.h>` for modern MSVC and all other platforms.
- Defines `FLAC__bool` as `int`.
- Defines `FLAC__byte` as `FLAC__uint8`.
- Undefines existing `true`/`false` macros and, for non-C++, defines `true` as `1` and `false` as `0`.

Implementation notes:
- This is a portability shim and contains no runtime logic.
- It intentionally creates libFLAC-owned type names rather than exposing raw C99 names throughout the public API.
- The `true`/`false` macro handling can affect translation units that include this header, but this is inherited libFLAC API behavior.

Filesystem relevance:
- No filesystem logic. It only supports portable public type definitions for the vendored libFLAC audio library in the 9front source tree.
