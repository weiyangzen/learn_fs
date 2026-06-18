# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/infback.c

## Purpose
Provides zlib’s callback-oriented inflate interface: `inflateBackInit_`, `inflateBack`, and `inflateBackEnd`. It is designed for callers that provide input and output callbacks and a caller-owned sliding window/output buffer.

## Main API Surface
- `inflateBackInit_(strm, windowBits, window, version, stream_size)` validates ABI/version, installs allocators, allocates `inflate_state`, and records the caller-provided window.
- `inflateBack(strm, in, in_desc, out, out_desc)` performs raw deflate block decoding using callback refill/flush.
- `inflateBackEnd(strm)` frees the inflate state.

## Implementation Notes
The file is largely copied from `inflate.c`, but it skips zlib/gzip wrapper parsing and works directly on deflate blocks. It supports stored blocks, fixed Huffman blocks, and dynamic Huffman blocks.

The state machine uses modes such as `TYPE`, `STORED`, `TABLE`, `LEN`, `DONE`, and `BAD`. Macros manage the bit accumulator, callback input pulls, and output-window flushing. When sufficient input and output are available, it calls `inflate_fast()` for optimized literal/length/distance decoding.

## Fixed Tables
`fixedtables()` either includes generated `inffixed.h` tables or builds them once when `BUILDFIXED` is defined. The built-on-demand path is explicitly not thread-safe because of static table initialization.

## Error Handling
Input callback failure or output callback failure returns `Z_BUF_ERROR`; `strm->next_in == Z_NULL` distinguishes input-denied cases. Invalid block structure returns `Z_DATA_ERROR` with `strm->msg` set. Invalid stream/state parameters return `Z_STREAM_ERROR`.

## Dependencies
Uses `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It shares the same decode table representation and inflate state as regular inflate.
