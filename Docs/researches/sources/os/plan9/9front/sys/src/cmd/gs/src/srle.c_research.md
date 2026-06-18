# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/srle.c

Implements the `RunLengthEncode` stream filter.

Key points:
- Initializes record-size tracking and pending-copy state from `srlx.h` inline helpers.
- Produces optimal legal run-length output by looking ahead enough to avoid splitting repeated runs prematurely.
- Emits literal runs with length byte `count - 1` and repeated runs with length byte `257 - run_length`.
- Honors optional record boundaries through `record_size`/`record_left`.
- Supports suspended literal copy state when output space is too small for a full literal packet.
- Emits EOD byte 128 on final input when `EndOfData` is true.

Dependencies and interactions:
- Uses `srlx.h` shared state and stream template declarations.

Research relevance:
- RunLength compressor counterpart to `srld.c`.
