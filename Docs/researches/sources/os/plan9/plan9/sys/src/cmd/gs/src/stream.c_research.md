# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.c

Purpose: implementation of Ghostscript’s stream abstraction, including allocation, GC descriptors, buffering, filters, string streams, and null filters.

Key contents:
- Defines stream and stream-state structure descriptors plus GC enumeration, relocation, and finalization.
- Implements `s_init`, `s_alloc`, `s_init_state`, `s_alloc_state`, `s_std_init`, `ssetfilename`, and `sfilename`.
- Implements generic reset/flush/close/disable behavior and filter close/flush propagation.
- Provides core APIs: `savailable`, `stell`, `spseek`, `sswitch`, `sclose`, `spgetcc`, `spputc`, `sungetc`, `sgets`, `sputs`, `spskip`, and `sreadline`.
- Implements buffer processing through `s_process_read_buf`, `s_process_write_buf`, private `sreadbuf`, private `swritebuf`, `stream_move`, and private `stream_compact`.
- Implements string streams: `sread_string`, `sread_string_reusable`, `swrite_string`, string seek/process helpers.
- Implements `swrite_position_only`.
- Implements filter setup/teardown: `s_init_filter`, `s_add_filter`, and `s_close_filters`.
- Defines `s_NullE_template` and `s_NullD_template`.

Dependencies: `stdio_.h`, `memory_.h`, `gdebug.h`, `gpcheck.h`, `stream.h`, `strimpl.h`.

Integration notes: this is the central runtime substrate for all stream filters, including the zlib filters in this batch. It also participates in Ghostscript GC relocation by updating buffer cursors after buffer movement.

Risks: stream pipeline traversal mutates `strm` links temporarily using reversible pointer walking; errors there could corrupt pipeline topology. Close/finalize behavior is deliberately conservative for file streams because non-file streams may free storage during close.
