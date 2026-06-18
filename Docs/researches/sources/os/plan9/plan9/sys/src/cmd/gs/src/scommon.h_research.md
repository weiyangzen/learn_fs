# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scommon.h

Common Ghostscript stream infrastructure definitions shared by stream clients and implementors.

It forward-declares `stream`, `stream_state`, and `stream_template`, then defines:

- Stream exceptional return codes: `EOFC`, `ERRC`, `INTC`, `CALLC`, and `max_stream_exception`.
- Read/write cursor structures used by stream processing procedures.
- Procedure signature macros for init, process, release, defaults, reinit, report-error, and parameter get/put functions.
- Generic `stream_state_common`, including template pointer, memory allocator, error reporter, `min_left`, and fixed-size error string.
- Base `stream_state` and GC descriptor declaration.

The file documents Ghostscript’s byte-oriented stream model and sticky exceptional conditions.

This is core stream framework code, not filesystem logic.
