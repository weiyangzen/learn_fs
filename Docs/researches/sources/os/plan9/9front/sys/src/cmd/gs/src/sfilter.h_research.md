# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sfilter.h

Defines state structures and templates for simple Ghostscript filters.

Key points:
- Documents the three sections of stream state: client-set parameters, initialization-computed values, and dynamic values.
- Defines `stream_exE_state` for eexec encoding, primarily the Type 1 encryption state.
- Defines `stream_exD_state` for eexec decoding, including binary/hex mode, `lenIV`, PFB linkage, odd hex digit, record limits, and skipped decoded bytes.
- Defines `stream_PFBD_state` for PFB record decoding and optional binary-to-hex translation.
- Defines `stream_SFD_state` for SubFileDecode, including EOD pattern, skip/count controls, and partial-match copy state.
- Provides GC descriptor macros and external stream template declarations for the filters implemented in `seexec.c` and `sfilter1.c`.

Research relevance:
- This header is the shared ABI for Level 1 simple stream filters in this Ghostscript source slice.
