# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.h

Defines scanner state and scanner API. `scanner_state` captures resumable parsing state: procedure stack depth, scanner options, current scan type, dynamic token buffer, and a union of substates for binary tokens, names, and string decoding filters.

Defines scanner options such as `SCAN_FROM_STRING`, `SCAN_CHECK_ONLY`, comment processing modes, PDF name rules, and PDF invalid-number compatibility. Defines special return codes: `scan_BOS`, `scan_EOF`, `scan_Refill`, `scan_Comment`, and `scan_DSC_Comment`.

Also exports `scan_token`, `scan_string_token_options`, `scan_handle_refill`, and comment hook pointers. This header deliberately exposes the full scanner state so callers can allocate it on the stack.
