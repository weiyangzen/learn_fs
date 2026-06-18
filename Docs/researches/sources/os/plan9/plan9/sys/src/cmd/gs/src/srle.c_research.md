# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srle.c

RunLengthEncode stream filter.

Key behavior:
- Initializes record size/remaining bytes and copy state from `srlx.h` inline macros.
- `s_RLE_process` emits optimal PackBits/PostScript-style run-length output by looking ahead enough to avoid prematurely breaking repeated runs.
- Encodes repeated runs as `257-run_length, byte`; literal runs as `run_length-1` followed by literal bytes.
- Supports logical record boundaries via `record_size`.
- Handles partial literal copying when the output buffer cannot hold a full literal record.
- Emits EOD byte `128` on final input when `EndOfData` is true.

Notable dependencies:
- Shared run-length state from `srlx.h`.

Research notes:
- The encoder intentionally does extra lookahead to generate optimal output for old conformance expectations.
- Minimum input size in the template is 129 to support lookahead and max literal-run decisions.
