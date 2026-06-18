# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scommon.h

Defines core Ghostscript stream types shared by stream clients and implementations. It introduces opaque `stream`, `stream_state`, and `stream_template`, stream exception return codes, read/write cursor layouts, stream procedure typedef macros, and generic parameter get/put procedure forms.

The generic `stream_state` contains the template pointer, memory allocator, error reporter, minimum lookahead, and an error string buffer. Comments explain stream exceptional-condition behavior and byte-oriented access conventions.

Dependencies include `gsmemory.h`, `gstypes.h`, and `gsstype.h`.

This is foundational userland stream infrastructure used by filters and file-like IO in Ghostscript.
