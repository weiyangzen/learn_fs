# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.h

Header for bounded Huffman stream filters.

It defines shared state containing generic Huffman state, an `hc_definition`, client-set `EndOfData` and `EncodeZeroRuns`, and dynamic `zeros` count. It defines:

- `max_zero_run`.
- `stream_BHCE_state` with an encode table.
- `stream_BHCD_state` with a decode table.
- GC descriptor macros for both states.
- Inline initialization macros `s_bhce_init_inline` and `s_bhcd_init_inline`.
- Decode state load/store macros for bit-reader state plus zero-run state.

This is compression-stream infrastructure, not filesystem code.
