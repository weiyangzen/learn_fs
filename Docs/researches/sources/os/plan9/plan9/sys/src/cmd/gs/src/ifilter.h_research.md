# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter.h

Defines interpreter-level filter creation support.

Key points:
- Includes `istream.h` and `ivmspace.h`.
- Declares `filter_read` and `filter_write`, which create stream filters from operator operands, a stream template, optional state, and VM-space metadata.
- Declares simplified no-parameter/no-state helpers `filter_read_simple` and `filter_write_simple`.
- Declares temporary-stream helpers `filter_mark_temp` and `filter_mark_strm_temp`.
- Declares `filter_report_error`, a standard filter error reporter that records messages in `$error.errorinfo`.
- Defines `stream_proc_state` for procedure-based streams, storing EOF state, current data index, procedure ref, and data ref.
- Provides GC descriptor macro `private_st_stream_proc_state()`.
- Declares `s_is_proc`.

Research relevance:
- Central adapter from PostScript filter operators to Ghostscript stream templates and VM allocation rules.
