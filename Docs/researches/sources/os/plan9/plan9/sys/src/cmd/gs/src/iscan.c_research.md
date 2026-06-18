# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.c

Purpose: implements the main Ghostscript PostScript/PDF token scanner. It reads tokens from streams or strings, builds refs, supports resumable scanning across stream refills/callouts, and handles Level 2 syntax extensions.

Main behavior:
- Dynamic string/name accumulation starts in an inline buffer and grows into VM strings as needed.
- `scan_token` skips whitespace, scans delimiters, names, literal names, immediate `//name` lookups, procedures delimited by `{}` with operand-stack accumulation, strings, hex strings, ASCII85 strings, comments, DSC comments, numbers, and binary tokens.
- `scan_string_token_options` scans from a string and advances the source string past the token.
- `scan_handle_refill` handles `scan_Refill` by processing stream buffers or pushing scanner continuation state to the execution stack for interrupts/callouts.
- Comment hooks can call external DSC/general comment processors or return comment tokens when scanner options request it.

State and continuation:
- `scanner_state` stores procedure stack depth, options, scan type, dynamic buffer, and scanner-specific substate.
- Suspended scans preserve partial comment/name/string/binary state and resume through labeled continuation paths.
- GC descriptors enumerate dynamic scanner strings and binary object-sequence arrays.

Important compatibility paths:
- Level 2 enables `<<`, `>>`, binary objects, ASCII85 strings, and broader string escape handling.
- PDF options alter name and invalid-number handling.
- The scanner can run in `SCAN_CHECK_ONLY` mode for syntax checking without producing full values.

Dependencies: stream/filter code, operand/dictionary stacks, name table, packed arrays, number scanner, binary token scanner, string decoders, VM-space store checks, and interpreter continuation machinery.
