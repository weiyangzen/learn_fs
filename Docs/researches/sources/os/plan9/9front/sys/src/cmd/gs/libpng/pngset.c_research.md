# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngset.c

This file implements libpng 1.2.8 setter/storage APIs for `png_info` and selected `png_struct` configuration fields. It is used by both readers and writers to store parsed PNG metadata or application-supplied metadata. It is not filesystem code.

Major responsibilities:
- Store simple metadata chunks: `png_set_bKGD`, `png_set_oFFs`, `png_set_pHYs`, `png_set_sBIT`, `png_set_sRGB`, `png_set_tIME`, `png_set_invalid`.
- Store validated color metadata: `png_set_cHRM`, `png_set_cHRM_fixed`, `png_set_gAMA`, `png_set_gAMA_fixed`, and `png_set_sRGB_gAMA_and_cHRM`.
- Validate and store IHDR via `png_set_IHDR`.
- Allocate/copy owned chunk payloads: `png_set_hIST`, `png_set_pCAL`, `png_set_sCAL`/`png_set_sCAL_s`, `png_set_PLTE`, `png_set_iCCP`, `png_set_text`/`png_set_text_2`, `png_set_tRNS`, `png_set_sPLT`, and `png_set_unknown_chunks`.
- Configure behavior: `png_set_keep_unknown_chunks`, `png_set_read_user_chunk_fn`, `png_set_rows`, `png_set_compression_buffer_size`, `png_set_asm_flags`, `png_set_mmx_thresholds`, and `png_set_user_limits`.

Control flow and data flow:
- Most setters return early on NULL `png_ptr` or `info_ptr`.
- `png_set_IHDR` validates dimensions, user limits, bit depth, color type, interlace, compression, and filter method, then derives channel count, pixel depth, and rowbytes.
- Palette, transparency, histogram, text, ICC profile, pCAL/sCAL, sPLT, and unknown chunks allocate storage and copy caller-provided data into libpng-owned buffers.
- Ownership is tracked with `info_ptr->free_me` flags when `PNG_FREE_ME_SUPPORTED` is enabled, otherwise by older `png_ptr->flags` bits for some data.
- Unknown chunk configuration appends five-byte entries: four-byte chunk name plus a per-chunk keep policy.
- Runtime tuning functions update zlib buffer size, assembler/MMX flags, and image dimension limits.

Notable implementation details:
- `png_set_PLTE` always allocates 256 palette entries, not just `num_palette`, preserving behavior for invalid files with oversized sample values.
- `png_set_tRNS` similarly allocates 256 transparency entries when byte alpha data is present.
- `png_set_text_2` grows the text array in batches and stores key/language/text strings in one contiguous allocation per text entry.
- `png_set_iCCP` frees any previous ICC data before storing a copied profile.
- `png_set_sPLT` appears to allocate/copy using `png_sizeof(png_sPLT_t)` for `entries`, although entries are `png_sPLT_entry`; this is inherited libpng 1.2-era code and is worth checking if auditing memory correctness.
- `png_set_unknown_chunks` records chunk location from current `png_ptr->mode`.

Important dependencies:
- Chunk data types and flags from `png.h`.
- Allocation/free helpers including `png_malloc`, `png_malloc_warn`, `png_free_data`, and `png_free`.
- Getter/setter pairings are exercised by `pngtest.c`.

Research notes:
- This file is the main metadata ownership boundary for libpng.
- It has no direct filesystem access.
- Audit attention should focus on allocation-size arithmetic, partial-allocation cleanup on error paths, ownership flags, and old compatibility branches.
