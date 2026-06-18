# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngset.c

`pngset.c` implements libpng setter/storage APIs for `png_info` and selected `png_struct` state. It is used both by readers, after chunk handlers parse file data, and by writers, when applications populate metadata before output.

Key responsibilities:
- Stores chunk metadata into `png_info` and sets the corresponding `PNG_INFO_*` validity flags.
- Copies caller-provided or parser-provided data into libpng-owned allocations where ownership must be retained.
- Validates high-risk inputs such as `IHDR`, gamma/chromaticity ranges, palette lengths, text arrays, unknown chunk storage, and user image-size limits.
- Configures ancillary behavior such as unknown chunk retention, user chunk callbacks, MNG feature permissions, row pointer ownership, write compression buffer size, assembler/MMX flags, and user width/height limits.

Implemented setter families:
- Basic metadata: `png_set_bKGD`, `png_set_hIST`, `png_set_oFFs`, `png_set_pHYs`, `png_set_PLTE`, `png_set_sBIT`, `png_set_tIME`, `png_set_tRNS`.
- Color management: `png_set_cHRM`, `png_set_cHRM_fixed`, `png_set_gAMA`, `png_set_gAMA_fixed`, `png_set_sRGB`, `png_set_sRGB_gAMA_and_cHRM`, `png_set_iCCP`.
- Calibration/scale: `png_set_pCAL`, `png_set_sCAL`, `png_set_sCAL_s`.
- Text and international text: public `png_set_text` plus internal `png_set_text_2`.
- Suggested palettes and unknown chunks: `png_set_sPLT`, `png_set_unknown_chunks`, `png_set_unknown_chunk_location`, `png_set_keep_unknown_chunks`.
- Runtime/configuration APIs: `png_permit_empty_plte`, `png_permit_mng_features`, `png_set_read_user_chunk_fn`, `png_set_rows`, `png_set_compression_buffer_size`, `png_set_invalid`, `png_set_asm_flags`, `png_set_mmx_thresholds`, and `png_set_user_limits`.

Important behavior:
- `png_set_IHDR` performs strict validation for zero dimensions, user dimension limits, bit-depth/color-type combinations, interlace method, compression method, filter method, and MNG intrapixel differencing exceptions. It also computes channels, pixel depth, and rowbytes.
- Palette and transparency setters allocate fixed 256-entry/byte buffers for historical compatibility with invalid PNG files that may reference out-of-range palette samples.
- `png_set_text_2` grows `info_ptr->text`, deep-copies key/language/translated-key/text data into one allocation per text entry, and tracks tEXt/zTXt/iTXt length fields according to compression mode.
- `png_set_unknown_chunks` appends deep copies of unknown chunk data and records the chunk location from `png_ptr->mode`.
- `png_set_sRGB_gAMA_and_cHRM` stores standard sRGB gamma and chromaticity values through the ordinary gAMA/cHRM setters.

Important dependencies and state:
- Includes `png.h` with `PNG_INTERNAL`.
- Uses libpng memory ownership flags such as `PNG_FREE_*`, `free_me`, and older fallback `png_ptr->flags` free markers.
- Called heavily from `pngrutil.c` chunk handlers and from applications or `pngtest.c` when copying metadata from read info to write info.

Edge cases and risks:
- Memory ownership is central. Many setters allocate deep copies and update `info_ptr->free_me`; partial allocation failure paths must avoid leaks and dangling partially initialized fields.
- `png_set_sPLT` uses `png_sizeof(png_sPLT_t)` when allocating/copying entries, although entries are `png_sPLT_entry` objects; this is a notable old-code maintenance risk.
- `png_set_text_2` frees the previous text array if reallocating fails, which preserves historical behavior but can surprise callers expecting old metadata to survive allocation failure.
- Public setters mostly return silently on null `png_ptr`/`info_ptr`; callers must not assume a failed setter reports an error.
