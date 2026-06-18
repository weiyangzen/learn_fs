# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/bitinput.c

Implements bitstream helpers for compressed DSS image decoding.

Key contents:
- Static Huffman decode tables `hufvals` and `huflens`.
- Static bit buffer state `buffer` and `bits_to_go`.
- `start_inputing_bits` resets bitstream state.
- `input_huffman` ensures six bits are buffered, decodes a Huffman code, and advances by the code length.
- `input_nybble` ensures four bits are buffered and returns a 4-bit value.

Behavior notes:
- Unexpected EOF is fatal and exits with `"format"`.
- Bit order is MSB-first within the accumulated buffer.
