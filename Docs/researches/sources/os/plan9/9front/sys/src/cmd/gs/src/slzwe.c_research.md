# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/slzwe.c

Implements the `LZWEncode` stream filter.

Key points:
- Uses fixed special codes 256 reset, 257 EOD, and 258 first assignable code.
- Maintains an encode table and open-addressed hash table keyed by prefix code plus next byte.
- Emits an initial reset code on first output.
- `lzw_put_code` writes variable-width 9..12-bit codes into the output bit buffer.
- When the table reaches a code-size threshold, either increases code width or emits a reset and rebuilds the table.
- On final input, emits the pending code, EOD code, and final partial byte if needed.

Dependencies and interactions:
- Shares `stream_LZW_state` and release/default handling with decode logic.

Research relevance:
- LZW compressor counterpart to `slzwd.c`.
