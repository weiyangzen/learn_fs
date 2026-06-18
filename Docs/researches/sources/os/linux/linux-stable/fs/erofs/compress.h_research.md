# File Research: sources/os/linux/linux-stable/fs/erofs/compress.h

## Summary
Defines EROFS decompression request structures, decompressor vtable, temporary page markers, and shared streaming helpers.

## Main Contents
- `struct z_erofs_decompress_req`
- `struct z_erofs_decompressor`
- `struct z_erofs_stream_dctx`
- Short-lived/preallocated page markers
- Decompressor registry declarations
- Crypto decompression hooks

## Important Details
Requests carry input/output page arrays, offsets, sizes, algorithm ID, in-place flags, partial-decoding flags, and allocation flags. Streaming decompressor state tracks current input/output page positions and bounce-buffer state.

## Risks
The same request structure supports software, crypto, in-place, partial, and sparse-output decompression, so flags must be interpreted consistently by each algorithm.
