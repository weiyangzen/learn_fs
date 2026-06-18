# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sfilter1.c

Implements Level 1 simple filters: `PFBDecode` and `SubFileDecode`.

Key points:
- `PFBDecode` parses PFB records starting with `0x80`, accepts text, binary, and EOF records, and reports errors for malformed record headers.
- Text PFB records translate carriage return to newline; binary records either pass bytes through or emit lowercase hexadecimal pairs depending on `binary_to_hex`.
- Record lengths are little-endian 32-bit values and are tracked across stream process calls.
- `SubFileDecode` supports raw byte-count operation when no EOD pattern is supplied, including initial skip handling.
- Pattern-mode `SubFileDecode` searches for an EOD byte sequence, supports skipping initial EOD occurrences, counts multiple EOD occurrences, and preserves partially matched bytes across output-buffer boundaries.
- Partial-pattern fallback uses longest-prefix matching against the EOD pattern.

Dependencies and interactions:
- Uses state definitions from `sfilter.h` and core stream cursor helpers from `strimpl.h`.

Research relevance:
- Provides basic font container decoding and substream extraction primitives used by higher PostScript/PDF filter stacks.
