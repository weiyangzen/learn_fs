# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibx.h

Purpose: public zlib stream state definition.

Key contents:
- Forward-declares `zlib_dynamic_state_t`.
- Defines `stream_zlib_state` with `stream_state_common`, decompression/compression parameters, and dynamic zlib state pointer.
- Declares public GC descriptor macro `public_st_zlib_state`.
- Declares `s_zlibD_template`, `s_zlibE_template`, and `s_zlib_set_defaults`.

Dependencies: stream state types from the stream subsystem.

Integration notes: included by clients that need to configure zlib filter parameters before initialization.

Risks: dynamic state is opaque; callers must use stream-template lifecycle hooks rather than managing it directly.
