# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/strimpl.h

Purpose: implementation-facing stream filter contract.

Key contents:
- Documents the `process` procedure semantics for input/output cursors and `last`.
- Defines the required return statuses: `EOFC`, `ERRC`, `0`, and `1`.
- Documents EOD lookahead behavior needed by decoding filters.
- Defines `struct stream_template_s`, including state type, init, process, min buffer sizes, release, set-defaults, and reinit hooks.
- Declares `stream_move` and hex decoding helper `s_hex_process`.
- Defines `hex_syntax` options.

Dependencies: `scommon.h`, `gstypes.h`, `gsstruct.h`.

Integration notes: zlib templates and null stream templates implement this contract.

Risks: filters must honor subtle buffer-boundary/EOD semantics or behavior changes depending on buffer size.
