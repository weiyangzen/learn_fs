# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.h

Public definition of Ghostscript streams.

Key points:
- Defines `stream_procs`, the virtual procedure table for availability, seek, reset, flush, close, process, and mode switching.
- Exposes `struct stream_s` for performance-sensitive clients.
- Stream state includes:
  - common stream state
  - read/write cursors
  - buffer pointer/size metadata
  - `end_status`
  - access modes
  - optional `cbuf_string`
  - logical position
  - stream procedure table
  - underlying stream for filters
  - temporary-stream flags
  - interpreter read/write IDs
  - file-list links
  - `CloseSource`/`CloseTarget` behavior
  - embedded stdio file state and subfile limits
- Defines mode and validity macros: `s_is_valid`, `s_is_reading`, `s_is_writing`, `s_can_seek`.
- Defines fast byte read/write macros `sgetc` and `sputc`.
- Declares buffer APIs, skip/seek APIs, inline read macros, allocation/init routines, string/file stream constructors, filename helpers, standard procedures, filter helpers, and NullEncode/Decode templates.
- `sbuf_min_left` encodes the filter read-ahead contract.

Dependencies and interactions:
- Includes `scommon.h` and `srdline.h`.
- Requires stdio setup through `stdio_.h` in implementation/users.
- Consumed by filters, file objects, devices, and data decoders.

Research relevance:
- This header is the stream ABI for the Ghostscript interpreter/library.
