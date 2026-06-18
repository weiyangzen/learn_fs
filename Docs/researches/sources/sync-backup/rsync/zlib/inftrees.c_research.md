# sources/sync-backup/rsync/zlib/inftrees.c

Purpose: builds canonical Huffman decode tables for inflate. It converts code-length arrays from fixed or dynamic deflate metadata into compact table entries used by the slow and fast decoders.

Important APIs/types/functions: exports `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)`. Local static base/extra arrays map deflate length codes and distance codes to base values and extra-bit operations. Return values are `0` for success, `-1` for invalid code length sets, and `+1` when the caller-provided table space is insufficient.

Control flow: `inflate_table` counts lengths, clamps root bits between minimum and maximum actual lengths, rejects over-subscribed and most incomplete trees, sorts symbols by length into `work`, then fills root-table and sub-table entries using deflate's bit-reversed canonical code ordering. It replicates shorter-code entries across all matching table slots and creates sub-table links when code lengths exceed the root. Remaining incomplete slots are marked invalid.

State and persistence: the function is stateless except for writes through `table`, `bits`, and `work`. It advances `*table` to the next free entry so callers can place length and distance tables back-to-back in `state->codes`. It exposes a copyright string but no mutable globals.

Dependencies and integration points: includes `zutil.h` and `inftrees.h`. Called by `inflate.c` for gzip/zlib dynamic block code-length tables, literal/length tables, distance tables, and optional fixed-table generation. Table sizing must align with `ENOUGH_LENS`, `ENOUGH_DISTS`, and root bit choices in `inflate.c`.

Risks: incorrect validation can accept invalid compressed data or reject valid streams. Used-entry accounting protects against table overrun; any root-bit or `ENOUGH` mismatch is memory-safety critical. The `op` encoding must remain consistent with both `inflate.c` and `inffast.c`.

Test signals: table-builder unit tests should cover empty, single-symbol, complete, incomplete, and over-subscribed length sets for `CODES`, `LENS`, and `DISTS`. Full inflate tests should include dynamic blocks with repeat-code-heavy length sections and maximum table sizes. Fuzzing should target dynamic headers.
