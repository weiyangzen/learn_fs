# sources/sync-backup/rsync/zlib/trees.c

Purpose: emits deflate blocks using stored, static Huffman, or dynamic Huffman coding. It consumes literal/match tallies from `deflate.c`, builds Huffman trees, serializes dynamic tree metadata, writes block bits into the pending buffer, and detects text/binary data type.

Important APIs and functions: internal exports are `_tr_init`, `_tr_tally`, `_tr_flush_block`, `_tr_flush_bits`, `_tr_align`, and `_tr_stored_block`. Major local helpers are `tr_static_init`, `init_block`, `pqdownheap`, `gen_bitlen`, `gen_codes`, `build_tree`, `scan_tree`, `send_tree`, `build_bl_tree`, `send_all_trees`, `compress_block`, `detect_data_type`, `bi_reverse`, `bi_flush`, `bi_windup`, and `copy_block`. It also defines fixed/static descriptor metadata and extra-bit tables.

Control flow: `_tr_init` prepares static tables and per-stream tree descriptors. Tallying appends symbols and frequency counts. `_tr_flush_block` builds literal and distance trees, builds the bit-length tree, computes byte costs for dynamic and static encodings, compares with stored-block cost, writes the selected block type, emits tree headers if dynamic, compresses symbol data, resets block state, and winds up bits for the final block.

State and persistence: mutates `deflate_state` tree arrays, heap, bit counts, symbol buffer cursor, match count, optimal/static bit lengths, bit buffer, and pending output. Static fixed tables are either generated once at runtime for non-ANSI/generation builds or included from `trees.h`.

Dependencies and integration points: includes `deflate.h` and optionally `trees.h`. It relies on `put_byte` and `deflate_state` from `deflate.h`; `deflate.c` relies on this file for all block emission. Output must match inflate's table builder and fixed-table expectations.

Risks: Huffman length overflow correction, dynamic tree repeat-code serialization, and stored/static/dynamic cost comparison are correctness-sensitive. Bit-buffer functions must preserve little-endian bit order required by deflate. The pending/symbol buffer overlay assertion protects against self-overwrite. Static initialization paths must remain thread-safe when using prebuilt `trees.h`; generation modes write `trees.h` as a build artifact.

Test signals: verify compression output round-trips through independent inflaters for stored, fixed, and dynamic blocks; force `Z_FIXED`; test high-frequency skew that causes bit-length overflow; test incompressible data that should become stored blocks; and compare generated `trees.h` under `GEN_TREES_H`. Sanitizers should cover block flushes near symbol buffer limits.
