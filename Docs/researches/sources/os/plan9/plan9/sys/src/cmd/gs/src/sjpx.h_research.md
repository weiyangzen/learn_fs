# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.h

Header for the JPXDecode stream filter.

Key contents:
- Defines `stream_jpxd_state` with JasPer image/stream pointers, output offset, non-GC memory pointer, compressed-data buffer, buffer size, and bytes filled.
- Declares GC structure macro and `s_jpxd_template`.

Notable dependencies:
- External JasPer API.
- `scommon.h` stream-state definitions.

Research notes:
- The comments document the central design constraint: JasPer lacks a public API for incremental pieces in this code path, so the full compressed stream is spooled before decoding.
