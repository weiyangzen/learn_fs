# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/infback.c

## Purpose
Provides zlib’s callback-based raw deflate inflater: `inflateBackInit_`, `inflateBack`, and `inflateBackEnd`.

## Key Elements
`inflateBackInit_` validates version/stream size/window parameters and stores a caller-provided sliding window. `inflateBack` drives a block-level inflate state machine over callback input/output functions. It handles stored, fixed-Huffman, and dynamic-Huffman blocks, builds decode tables with `inflate_table`, and delegates fast decode to `inflate_fast` when enough input/output space exists. `inflateBackEnd` frees state.

## Behavior/Risks
This API does not parse zlib or gzip wrappers; callers are responsible for wrapping/checking if needed. Input callback failure and output callback failure both surface as `Z_BUF_ERROR`, with `strm->next_in == Z_NULL` helping distinguish input failure. Dynamic-table and distance validation errors set messages such as invalid block type, invalid bit length repeat, invalid distance code, or distance too far back. The fixed-table builder can be runtime-generated under `BUILDFIXED`, noted as not thread-safe.

## Dependencies
Includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Shares `struct inflate_state` and Huffman decode tables with the normal streaming inflater.
