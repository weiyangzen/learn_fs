# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.c

This file implements stream buffer state management and error string conversion. `mad_stream_init` clears buffer pointers, skip length, sync/free-rate state, frame pointers, bit pointers, ancillary data, Layer III main-data reservoir pointer/length, options, and error status. `mad_stream_finish` frees the Layer III main-data buffer if allocated.

`mad_stream_buffer` installs a caller-owned input buffer, sets `bufend`, initializes current/next frame pointers, marks sync as available, and initializes the bit pointer. `mad_stream_skip` accumulates byte skip requests used by header decode and metadata skipping. `mad_stream_sync` scans from the current bit pointer's next byte until it finds an MPEG sync pattern (`0xff` followed by high `0xe0` bits), requiring the guard-byte margin before declaring success.

`mad_stream_errorstr` maps every `enum mad_error` value to a human-readable string used by `main.c` debug logging. This file does not read from file descriptors itself; it only manages memory ranges supplied by the input callback.
