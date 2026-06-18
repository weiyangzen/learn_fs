# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/codebook.c

This file implements Vorbis codebook bitstream serialization and runtime encode/decode operations. It depends on Ogg bitpacking (`ogg/ogg.h`), Vorbis public codec types, `codebook.h`, scaling helpers, memory helpers from `misc.h`, and portability macros from `os.h`.

Main routines:
- `vorbis_staticbook_pack()` writes a `static_codebook` to an Ogg packet buffer. It emits the Vorbis codebook sync pattern `0x564342`, dimensions, entry count, length-list encoding, map type, and quantization metadata/list for maptypes 1 and 2.
- `vorbis_staticbook_unpack()` reads the packed form back into an allocated `static_codebook`, validating sync, dimensions/entries bit budget, ordered/unordered length-list encoding, map type, quantization bit budget, and EOF conditions.
- `vorbis_book_encode()` writes a codeword from an initialized runtime `codebook`.
- `decode_packed_entry_number()` is the central decode helper. It uses a first-stage lookup table (`dec_firsttable`) where possible, then falls back to bit-reversed binary search over ordered codewords.
- `vorbis_book_decode()` returns the original entry number via `dec_index`.
- `vorbis_book_decodevs_add()`, `vorbis_book_decodev_add()`, `vorbis_book_decodev_set()`, and `vorbis_book_decodevv_add()` decode vector values and add/set them into mono, vector, or channel-interleaved output buffers.

Serialization behavior:
- Codeword lengths can be packed in ordered or unordered form. Ordered books store the initial length and run counts per length; unordered books either store all lengths directly or store a used/unused bit before each nonzero length.
- Maptype 0 has no value mapping.
- Maptype 1 stores a compact implicit lattice quant list sized by `_book_maptype1_quantvals()`.
- Maptype 2 stores an explicit `entries * dim` quant list.
- Unsupported map types return errors on pack/unpack.

Decode behavior:
- The bitstream is LSB-packed, but the optimized decode path needs MSB-first comparisons, so `bitreverse()` is used before binary-search comparison.
- The first table either maps directly to an entry or encodes a search interval using high-bit tagging.
- On decode miss or EOF, functions return `-1`; otherwise vector decode routines use `book->valuelist + entry * book->dim`.

Integration points:
- `info.c` calls `vorbis_staticbook_unpack()` while reading setup headers and `vorbis_staticbook_pack()` while writing them.
- `block.c` initializes runtime encode/decode `codebook` arrays from `static_codebook` descriptors.
- `res0.c`, `floor0.c`, and `floor1.c` call the decode/encode helpers for residue and floor data.
- `sharedbook.c` owns memory cleanup, value-list generation, codeword generation, and decode lookup table construction used by this file.

Risk and edge cases:
- The unpacker performs several explicit bounds checks against remaining packet storage before allocating and reading large lists, which is important for malformed stream handling.
- Allocation failures are not consistently checked after `malloc()` / `_ogg_malloc()` in this older C code path.
- Vector decode routines assume upper layers guard dimension granularity; the comments explicitly say most callers must ensure `n` is compatible with `book->dim`.
- `vorbis_book_decodevs_add()` allocates temporary arrays per call, so hot residue decode paths may be sensitive to allocator behavior.
- `vorbis_book_encode()` assumes the runtime codebook was initialized correctly and writes `lengthlist[a]` bits from `codelist[a]`.

Testing/review signals:
- Exercise setup-header round trips: static book pack, unpack, init decode, clear.
- Fuzz malformed setup packets around ordered length runs, unused-entry tags, maptype 1/2 quant lengths, zero dimensions, and truncated packets.
- Decode tests should cover first-table direct hits, first-table interval fallback, single-entry books, sparse books with `dec_index`, and vector add/set paths used by floor and residue backends.
