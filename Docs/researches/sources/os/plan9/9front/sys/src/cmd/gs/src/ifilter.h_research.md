# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter.h

Defines interpreter-level filter creation support.

Key points:
- Includes `istream.h` and `ivmspace.h`.
- Declares `filter_read` and `filter_write`, which create stream filters from operator operands, a stream template, optional state, and VM-space metadata.
- Declares simplified no-parameter/no-state helpers:
  - `filter_read_simple`
  - `filter_write_simple`
- Declares temporary-stream helpers:
  - `filter_mark_temp`
  - `filter_mark_strm_temp`
- Declares `filter_report_error`, a standard stream error reporter that records messages in `$error.errorinfo`.
- Defines `stream_proc_state` for procedure-based streams, containing `eof`, current data index, interpreter procedure ref, and data ref.
- Provides GC descriptor macro `private_st_stream_proc_state()`.
- Declares `s_is_proc` to detect procedure-based streams.

Dependencies and interactions:
- Filter operators in `zf*.c` use this to construct PostScript filter streams.
- Procedure streams are interpreter-level because they store refs/procedures, unlike lower-level stream package filters.

Research relevance:
- Central adapter from PostScript filter operators to Ghostscript stream templates and VM allocation rules.
