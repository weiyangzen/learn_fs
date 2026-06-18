# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.c

Implements the Ghostscript PostScript token scanner. It reads tokens from streams or strings, handling whitespace, comments, names, literal names, immediate lookup names, numbers, arrays/procedures, strings, hex strings, ASCII85 strings, Level 2 delimiters, binary tokens, EOF, and stream errors.

The scanner is resumable. It stores partial state in `scanner_state` when input refill, VM allocation failure, interrupts, or stream callouts occur. Dynamic token text is managed with `dynamic_area`, initially using an embedded buffer and growing to heap storage when needed. Procedure bodies are accumulated on the operand stack until matching `}` and can be packed arrays when `ref_array_packing` is enabled.

Important entry points are `scanner_state_init_options`, `scan_token`, `scan_string_token_options`, and `scan_handle_refill`. Comment handling is pluggable through `scan_dsc_proc` and `scan_comment_proc`, or returned as scanner status codes when options request it. Number parsing is delegated to `scan_number`; binary tokens are delegated to `scan_binary_token`.
