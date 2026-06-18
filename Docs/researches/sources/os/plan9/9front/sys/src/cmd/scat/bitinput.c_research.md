# File Research: sources/os/plan9/9front/sys/src/cmd/scat/bitinput.c

Purpose: Bitstream decoder support for DSS compressed image input used by `scat`.

Key routines:
- `start_inputing_bits`: resets bit-buffer state.
- `input_huffman`: reads enough bits to index a 6-bit Huffman table, consumes the table-specified bit length, and returns the decoded 4-bit value.
- `input_nybble`: reads a raw 4-bit nybble.

Data: `hufvals` and `huflens` define a compact Huffman decode table.

Integration: Called by `qtree.c` and `dssread.c` during DSS q-tree bit-plane decoding.

Risks:
- Uses file-static `buffer` and `bits_to_go`, so decoding is single-stream and stateful.
- Unexpected EOF exits with `"format"`.
