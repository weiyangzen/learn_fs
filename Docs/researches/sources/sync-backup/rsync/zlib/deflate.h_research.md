# sources/sync-backup/rsync/zlib/deflate.h

Purpose: private compressor-state header for the vendored zlib implementation. It is not an application API; it defines DEFLATE constants, tree descriptor types, the full `deflate_state` layout, and inline tally/output helpers shared by `deflate.c` and `trees.c`.

Important APIs/types/functions: key constants include `LENGTH_CODES`, `LITERALS`, `L_CODES`, `D_CODES`, `BL_CODES`, `HEAP_SIZE`, `MAX_BITS`, `Buf_size`, stream status values, `MIN_LOOKAHEAD`, `MAX_DIST`, and `WIN_INIT`. Important types are `ct_data`, `tree_desc`, `Pos`, `IPos`, and `deflate_state`. It declares internal tree functions `_tr_init`, `_tr_tally`, `_tr_flush_block`, `_tr_flush_bits`, `_tr_align`, and `_tr_stored_block`. Non-debug builds inline `_tr_tally_lit` and `_tr_tally_dist` to append three-byte symbols and update frequency trees.

Control flow: there is no runtime control flow beyond macros. The header shapes the control flow in `deflate.c`: stream status values drive wrapper/header states, `put_byte` appends pending bytes, distance-code mapping routes matches to `_dist_code`, and the tally macros decide when a block must flush by comparing `sym_next` to `sym_end`.

State and persistence: `deflate_state` is the persistent compression object. It stores the public stream back-pointer, pending output, wrapper/header fields, LZ77 window/hash structures, match-search cursors, compression tuning values, Huffman trees, heap/work arrays, symbol buffer cursors, debug counters, bit buffer, and `high_water` memory-initialization marker. No external persistence exists; state survives across calls until reset or end.

Dependencies and integration points: includes `zutil.h` and therefore pulls in public zlib types, allocation macros, checksum helpers, and portability configuration. It exposes the contract between compressor match generation and Huffman block emission in `trees.c`; changes to structure layout or macros must be synchronized with both files.

Risks: this header is a blast-radius multiplier. Field order and meanings are assumed by copy/reset logic and tree code. The overlaid `pending_buf`/`sym_buf` model depends on `lit_bufsize`, `sym_end`, and three-byte symbols. Changing constants like `MAX_BITS`, `MIN_LOOKAHEAD`, or distance coding breaks RFC1951 compatibility and table sizes. Inline macros evaluate some arguments multiple times and require side-effect-free inputs where documented.

Test signals: compile with debug and non-debug modes, `FASTEST`, optional gzip disablement, and representative platform defines. Compression tests should verify block flushes, distance/length tallying, and `deflateCopy` after partially filled buffers because these paths depend directly on this header's state layout.
