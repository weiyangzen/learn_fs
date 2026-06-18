# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/sharedbook.c

Shared Vorbis codebook helper implementation for codeword generation, float packing, quantization maps, and encode/decode initialization.

Important routines:
- `ov_ilog()` returns integer bit width.
- `_float32_pack()` and `_float32_unpack()` convert Vorbis non-IEEE packed float representation.
- `_make_words()` builds canonical Huffman codewords from length lists, including sparse and single-entry cases.
- `_book_maptype1_quantvals()` computes maptype-1 quantization value count with integer verification.
- `_book_unquantize()` expands maptype 1/2 quant lists into floating value lists.
- `vorbis_staticbook_destroy()` frees heap-allocated static codebooks.
- `vorbis_book_clear()` frees runtime codebook lookup fields.
- `vorbis_book_init_encode()` initializes encode-side codebook fields.
- `vorbis_book_init_decode()` builds sorted bit-reversed decode lookup structures and first-level decode tables.
- `vorbis_book_codeword()` and `vorbis_book_codelen()` expose encode-side codeword metadata.

Integration points:
- Used by `codebook.c`, `info.c`, residue/floor setup, and static book initialization.
- Depends on `codebook.h`, `scales.h`, `ogg/ogg.h`, and `os.h`.

Risk and review signals:
- `_make_words()` rejects overpopulated and most underpopulated Huffman trees; this is security-critical for setup parsing.
- `_float32_pack()` notes it does not guard under/overflow.
- Decode initialization has several heap allocations without explicit failure handling.
- Correctness is bitstream-critical; floating-point changes can affect compatibility.

Filesystem relevance:
- No filesystem logic. It is codec codebook infrastructure.
