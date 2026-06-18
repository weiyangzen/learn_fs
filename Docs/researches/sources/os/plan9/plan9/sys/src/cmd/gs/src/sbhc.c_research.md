# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.c

Implementation of bounded Huffman encode/decode stream filters.

The bounded Huffman filters extend generic Huffman coding with optional zero-run encoding and an optional end-of-data marker.

Important encode behavior:

- `s_BHCE_init` allocates an encoding table from the provided Huffman definition and calls `hc_make_encoding`.
- `s_BHCE_process` encodes byte values, accumulates runs of zero when configured, emits run-length symbols, and optionally emits an EOD code at finalization.
- `s_BHCE_release` frees the allocated encoding table.

Important decode behavior:

- `s_BHCD_init` allocates a decoding table sized by `hc_sizeof_decoding` and calls `hc_make_decoding`.
- `s_BHCD_process` decodes variable-length codes, expands zero runs, and recognizes the configured EOD code.
- Some comments flag incomplete or questionable paths, including “WRONG” allocation comments and a not-yet-implemented partial-code case.

The stream templates are `s_BHCE_template` and `s_BHCD_template`.

This is compression filter code, not filesystem logic.
