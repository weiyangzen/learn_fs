# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.c

Huffman utility implementation for generating bounded canonical code definitions and encode/decode tables.

Key behavior:
- `hc_compute` builds a Huffman tree from value frequencies, computes code lengths, bounds lengths to `def->num_counts`, sorts values into canonical order, and fills `counts` and `values`.
- `hc_limit_code_lengths` adjusts too-long code lengths while maintaining a full prefix code.
- `hc_bytes_from_definition` compresses a well-behaved Huffman definition into run-length bytes of value-count/code-length pairs.
- `hc_sizes_from_bytes` computes definition array sizes from that compressed representation.
- `hc_definition_from_bytes` expands compressed bytes back into canonical counts and value order.
- `hc_make_encoding` builds canonical code/code-length entries by decoded value.
- `hc_sizeof_decoding` computes storage required for two-level decode tables.
- `hc_make_decoding` fills first-level and auxiliary decode table entries.

Notable dependencies:
- Memory and error APIs: `gsmemory.h`, `gserror.h`, `gserrors.h`.
- Huffman definitions from `shc.h`.

Research notes:
- `hc_definition_from_bytes` appears to contain a loop typo: `for (j = 0; j < n; n++)` increments `n` instead of `j`, which would not terminate normally for positive `n` and would corrupt expansion if used.
- Allocation failure in `hc_compute` correctly returns `gs_error_VMerror`.
