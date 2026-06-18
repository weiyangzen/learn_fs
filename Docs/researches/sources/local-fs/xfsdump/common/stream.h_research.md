# File Research: sources/local-fs/xfsdump/common/stream.h

## Role

This header declares stream tracking constants, states, exit codes, and APIs.

## Constants

- `STREAM_SIMMAX` is 20 simultaneous streams.
- Stream exit codes distinguish success, stop, abort, and core request.
- `stream_state_t` has free, running, and zombie states.

## API

The header declares initialization, registration, death/freeing, lookup, exit-status setters, exit-status query, and active stream counting.

One declaration, `stream_exists()`, appears in the header but is not implemented in the read `stream.c`.
