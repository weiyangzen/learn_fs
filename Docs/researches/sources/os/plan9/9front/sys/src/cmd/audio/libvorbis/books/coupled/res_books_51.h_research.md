# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7052, source bytes 262111, report `Docs/researches/chunks/chunk_sources_os_plan9_9front_sys_src_cmd_audio_libvorbis_books_coupled_res_bo_76c5ded57884_research.md`
- chunk 2: lines 7053-12273, source bytes 197481, report `Docs/researches/chunks/chunk_sources_os_plan9_9front_sys_src_cmd_audio_libvorbis_books_coupled_res_bo_37f115d9e336_research.md`

## Chunk Research

### Chunk 1: lines 1-7052

# Chunk Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h lines 1-7052

## Scope

- Subset: `Docs/research_subset_a.md`, which includes `sources/os/plan9/9front`.
- File chunk read: `sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h`, lines 1-7052.
- This is an oversized generated/static-data header for Ogg Vorbis 5.1 surround residue codebooks. No final per-file report was created.

## APIs And Symbols

- This chunk declares only `static const` data; it exports no functions, macros, or externally linked symbols.
- All symbols have internal linkage because the header defines `static const` objects intended to be included by libvorbis mode templates.
- Primary data type dependency is `static_codebook` from `codebook.h`, with fields for vector dimension, entry count, Huffman length list, map type, quantization parameters, quant list, and allocation flag.
- VQ codebook pattern:
  - `_vq_quantlist__...[]`: `long` quantization value lists.
  - `_vq_lengthlist__...[]`: `char` Huffman/codeword length tables; zero entries mean unused/sparse codebook entries.
  - `_44p*_...`: `static_codebook` descriptors that bind a length list, maptype `1`, packed quantization parameters, and a quant list.
- Huffman-only pattern:
  - `_huff_lengthlist__...[]`: `char` codeword lengths.
  - `_huff_book__...`: `static_codebook` descriptors with maptype `0` and `NULL` quantlist.

## Data Covered

- Header/license block: lines 1-15 identify this as Xiph.Org OggVorbis source, function "static codebooks for 5.1 surround".
- Complete book families in this chunk:
  - `_44p0_*` and `_huff_book__44p0_*`: lines 17-898.
  - `_44p1_*` and `_huff_book__44p1_*`: lines 901-1782.
  - `_44p2_*` and `_huff_book__44p2_*`: lines 1785-2914.
  - `_44p3_*` and `_huff_book__44p3_*`: lines 2917-4046.
  - `_44p4_*` and `_huff_book__44p4_*`: lines 4049-5178.
  - `_44p5_*` and `_huff_book__44p5_*`: lines 5181-6310.
- Partial `_44p6_*` family in this chunk:
  - Complete through `_44p6_p4_1`: lines 6313-6977.
  - `_vq_quantlist__44p6_p5_0`: lines 6979-6985 complete.
  - `_vq_lengthlist__44p6_p5_0`: starts at line 6987 and is incomplete at chunk end line 7052.
- The chunk contains 107 complete `static_codebook` definitions before the split and one incomplete array definition at the split boundary.

## Control Flow

- There is no direct runtime control flow in this chunk.
- Runtime use is indirect:
  - `modes/residue_44p51.h` includes this header.
  - `static_bookblock` tables in `residue_44p51.h` reference these `_44p*_*` `static_codebook` objects.
  - `vorbis_encode_residue_setup()` in `vorbisenc.c` walks residue template book blocks, deduplicates pointers with `book_dup_or_new()`, sets residue `secondstages`, fills `booklist`, and installs the selected `static_codebook` pointers into `codec_setup_info.book_param`.
  - `codebook.c` / `sharedbook.c` then pack, unpack, initialize, or unquantize codebooks using the `static_codebook` fields.

## State

- State is immutable compile-time data:
  - `lengthlist` arrays define canonical code lengths.
  - `quantlist` arrays define scalar quant values for maptype 1 VQ books.
  - `static_codebook` descriptors bind dimensions/entry counts to the backing arrays.
- The only mutable state affected downstream is encoder setup state outside this header (`codec_setup_info`, residue `booklist`, `groupbook`, and `secondstages`) when mode templates choose these codebooks.
- `allocedp` is initialized to `0` for all descriptors, indicating backing arrays are static and should not be freed as owned dynamic allocations.

## Dependencies

- Requires `static_codebook` to be visible before inclusion; this is satisfied through the libvorbis mode include chain.
- Uses `NULL`, so including translation units must provide it through surrounding headers.
- Consumed by `sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44p51.h`.
- The codebook interpretation depends on libvorbis internals in:
  - `codebook.h` for structure layout.
  - `codebook.c` for static book packing/unpacking.
  - `sharedbook.c` for quantization/unquantization and encode/decode initialization.
  - `vorbisenc.c` for residue template installation into encoder setup.

## Risks And Invariants

- Generated-data integrity is the main risk. Each `static_codebook.entries` value must match its `lengthlist` element count, and maptype 1 quant list size must match the implied quant value count for `dim` and `entries`.
- This chunk shows common dimensions/entry counts: `1x7`, `1x25`, `2x4`, `2x9`, `2x25`, `2x49`, `2x64`, `2x169`, `5x243`, and `5x3125`.
- Sparse books intentionally contain many zero code lengths, especially low-partition books such as `_44p0_p1_0`, `_44p1_p1_0`, and several `_p2_0` books.
- The old-style casts from `const char *`/`const long *` to non-const fields mirror libvorbis' `static_codebook` definition. Consumers must preserve read-only treatment for these static arrays.
- Manual edits are high risk because a single length, count, or quantization parameter mismatch can corrupt bitstream compatibility or cause decode/encode table construction failures.
- Chunk boundary risk: line 7052 cuts through `_vq_lengthlist__44p6_p5_0`; no conclusion about `_44p6_p5_0` or later `_44p6` books should be made from this chunk alone.

## Cross-Chunk References

- Next chunk must continue `_vq_lengthlist__44p6_p5_0` from line 7053, close the array, and define `_44p6_p5_0`.
- Later `_44p6` symbols expected by `residue_44p51.h` but not complete in this chunk include `_44p6_p5_0`, `_44p6_p5_1`, `_44p6_p6_0`, `_44p6_p6_1`, `_44p6_p7_0`, `_44p6_p7_1`, `_44p6_p7_2`, `_44p6_p7_3`, and `_huff_book__44p6_short`.
- Later chunks also contain complete `_44p7`, `_44p8`, `_44p9`, and `_44pn1` families, which are referenced by the same residue template header.
- The final merged file report should connect all chunks to the residue blocks and templates in `modes/residue_44p51.h`, but that merge is intentionally outside this chunk's scope.

### Chunk 2: lines 7053-12273

# Chunk Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/books/coupled/res_books_51.h lines 7053-12273

## Scope

This chunk is within subset A because `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. The covered line range is a generated/static Vorbis residue codebook section from 9front's imported `audio/libvorbis` tree. It contains data declarations only: no executable functions, no macros, and no direct filesystem or kernel logic.

## APIs and Symbols

The public surface visible in this chunk is a set of file-local `static const` arrays and `static const static_codebook` descriptors. These are not exported APIs; they are included by libvorbis setup code elsewhere in the same header/translation unit.

Primary codebook descriptors in this chunk:

- Partial continuation of `_44p6` plus `_44p6_p5_0` at line 7186, `_44p6_p5_1` at 7208, `_44p6_p6_0` at 7241, `_44p6_p6_1` at 7274, `_44p6_p7_0` at 7307, `_44p6_p7_1` at 7340, `_44p6_p7_2` at 7381, `_44p6_p7_3` at 7422, and `_huff_book__44p6_short` at 7437.
- Full `_44p7` family: LFE/long Huffman books and vector quantization books from `_44p7_l0_0` at 7475 through `_huff_book__44p7_short` at 8572.
- Full `_44p8` family: `_44p8_l0_0` at 8610 through `_huff_book__44p8_short` at 9889.
- Full `_44p9` family: `_44p9_l0_0` at 9927 through `_huff_book__44p9_short` at 11382.
- Beginning and most of `_44pn1` family: `_44pn1_l0_0` at 11420 through `_huff_book__44pn1_short` at 12266.

Each VQ book follows the same pattern: `_vq_quantlist__...` arrays hold quantization values, `_vq_lengthlist__...` arrays hold codeword lengths, and `static_codebook` initializers bind dimensions, entry counts, map type, quant metadata, and quant-list pointers. Huffman-only books use `_huff_lengthlist__...` plus `static_codebook` descriptors with map type `0` and `NULL` quant lists.

## Control Flow

There is no local control flow. Runtime behavior is entirely data-driven by libvorbis code that consumes `static_codebook` structures. The effective flow is: higher-level setup tables select a family such as `_44p7`, `_44p8`, `_44p9`, or `_44pn1`; decoder/encoder setup passes the selected book to Vorbis codebook initialization; that layer interprets canonical code lengths and quantization metadata.

## State and Data Model

All state is immutable static storage. VQ descriptors are mostly dimension `5` with `243` or `3125` entries; scalar selector books use dimension `1` with `7` or `25` entries; low-frequency setup books use dimension `2` with `169`, `25`, `9`, or similar entry counts. Several `_44pn1` length lists are sparse and use `0` to mark disabled codebook entries.

## Dependencies

This chunk depends on the `static_codebook` definition, `NULL`, and Vorbis codebook initialization/lookup routines that understand map type `0`, map type `1`, length lists, packed quantization fields, and quant lists. It has no direct dependency on Plan 9 syscalls, filesystems, VFS objects, storage devices, or kernel APIs.

## Cross-Chunk References

- The chunk starts mid-declaration: lines 7053-7185 are the tail of `_vq_lengthlist__44p6_p5_0`, whose declaration begins in the previous chunk. Its `static_codebook _44p6_p5_0` is completed at line 7186.
- Families `_44p6`, `_44p7`, `_44p8`, `_44p9`, and `_44pn1` are likely referenced by aggregate residue book arrays later in this header or companion generated headers.
- `_44pn1` continues only through `_huff_book__44pn1_short` in this range; any later related declarations are in the next chunk.

## Risks and Review Notes

Generated-data integrity is the main risk. A single changed integer can silently alter codec bitstream compatibility or audio quality. Entry counts in `static_codebook` initializers must match corresponding length-list sizes. The `char *` casts discard `const`, following older libvorbis style, and rely on consumers treating static tables as read-only. Sparse `_44pn1` books require consumers to interpret zero length as “unused,” not as a valid code.

## Filesystem Relevance

No filesystem implementation behavior is present in this chunk. Its subset A relevance is repository placement under `sources/os/plan9/9front`; functionally it is user-space audio codec static data.
