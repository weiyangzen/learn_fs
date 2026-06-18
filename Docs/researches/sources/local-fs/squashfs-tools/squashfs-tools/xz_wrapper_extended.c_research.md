# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper_extended.c

## Purpose

`xz_wrapper_extended.c` implements the Squashfs compressor adapter for XZ/LZMA2 using liblzma, with OpenWrt-style extended XZ options. It registers the `xz` compressor through `struct compressor xz_comp_ops` and provides the full compressor lifecycle used by `mksquashfs` and extraction paths: parse `-X` options, post-process options once block size is known, serialize compressor options into the Squashfs image, restore stored options during append mode, display stored options, initialize compression streams, compress, uncompress, and print usage.

## Main State

The file uses process-global static option state:

- `bcj[]`: table of supported BCJ filters: `x86`, `powerpc`, `ia64`, `arm`, `armthumb`, `sparc`, `arm64`, `riscv`.
- `filter_count`: number of compression candidates to try. It starts at `1` for plain LZMA2 without BCJ.
- `dictionary_size`: final XZ dictionary size for data blocks.
- `dictionary_percent`: deferred percentage form for `-Xdict-size`.
- `preset`: liblzma preset level and optional `LZMA_PRESET_EXTREME`.
- `lc`, `lp`, `pb`: optional LZMA literal/context/position tuning overrides, initialized to `-1` when unspecified.

The global state means this adapter is designed for the single compressor configuration flow used by the Squashfs tools, not for independent concurrent compressor configurations.

## Compatibility Guards

The file defines fallback numeric IDs for newer liblzma filters when building against older headers:

- `LZMA_FILTER_ARM64` fallback, added upstream in liblzma 5.4.0.
- `LZMA_FILTER_RISCV` fallback, added upstream in liblzma 5.6.0.

Runtime support is still checked with `lzma_filter_encoder_is_supported()` when users request BCJ filters.

## Option Parsing

`xz_options()` recognizes seven compressor options:

- `-Xbcj filter1,filter2,...`
- `-Xdict-size <dict-size>`
- `-Xpreset <preset-level>`
- `-Xe`
- `-Xlc <value>`
- `-Xlp <value>`
- `-Xpb <value>`

Return contract:

- `>= 0`: recognized and parsed, value is number of extra argv entries consumed.
- `-1`: unrecognized option.
- `-2`: recognized option with invalid or missing argument.

### `-Xbcj`

`-Xbcj` parses a comma-separated list of BCJ filter names. Each selected filter is marked in `bcj[i].selected`, and `filter_count` is incremented only once per unique filter. The parser also checks liblzma encoder support for each selected filter.

The selected BCJ filters are tried in addition to the no-filter LZMA2 path, and the shortest compressed result is chosen later in `xz_compress()`.

### `-Xdict-size`

`-Xdict-size` accepts either:

- An absolute integer value, optionally suffixed with `K/k` or `M/m`.
- A percentage of block size, using `%`.

Fractional values are allowed only for percentages. The option does not fully validate final size immediately because block size may be parsed later by `mksquashfs`; final validation happens in `xz_options_post()`.

### `-Xpreset` and `-Xe`

`-Xpreset` sets the liblzma preset level after validating it against `LZMA_PRESET_LEVEL_MASK`. `-Xe` ORs `LZMA_PRESET_EXTREME` into the preset flags.

### `-Xlc`, `-Xlp`, `-Xpb`

These options override LZMA parameters after preset setup and after BCJ-specific parameter adjustments. Ranges are validated with liblzma constants:

- `lc`, `lp`: `LZMA_LCLP_MIN` through `LZMA_LCLP_MAX`.
- `pb`: `LZMA_PB_MIN` through `LZMA_PB_MAX`.

## Post-Processing

`xz_options_post(int block_size)` finalizes `dictionary_size`.

If `-Xdict-size` was specified:

- Absolute dictionary size must be `<= block_size`.
- Percentage dictionary size is computed from `block_size`.
- Final dictionary size must be at least `8192`.
- Final dictionary size must be representable in the XZ header as either `2^n` or `2^n + 2^(n+1)`.

If no dictionary size was specified, `dictionary_size` defaults to `block_size`.

This representability check is important because Squashfs stores and later restores XZ options for append compatibility.

## Filesystem Option Serialization

`xz_dump_options(int block_size, int *size)` returns `NULL` when default options are being used:

- Data block dictionary size equals `block_size`.
- No BCJ filter selected, meaning `filter_count == 1`.

Otherwise it builds a static `struct comp_opts` with:

- `dictionary_size`
- `flags`, one bit per BCJ table entry

The structure is byte-swapped through `SQUASHFS_INSWAP_COMP_OPTS()` before returning.

A subtle point: `preset`, `-Xe`, `lc`, `lp`, and `pb` affect compression behavior but are not serialized here. The serialized Squashfs compressor options preserve dictionary size and BCJ flags only.

## Append-Mode Option Extraction

`xz_extract_options(int block_size, void *buffer, int size)` restores compressor state from stored filesystem options.

If `size == 0`, it forces defaults:

- `dictionary_size = block_size`
- no BCJ flags

Otherwise it requires the stored option size to equal `sizeof(struct comp_opts)`, byte-swaps the structure, reads dictionary size and flags, validates dictionary-size representability, and reconstructs `bcj[].selected` plus `filter_count`.

This explicit reset is used so append mode ignores user-supplied `-X` options and matches the original filesystem compressor settings.

Potential edge case: dictionary representability checks compute `n = ffs(dictionary_size) - 1` before guarding against `dictionary_size == 0`. A corrupt stored option with zero dictionary size could make that expression produce a negative shift in later checks. The same pattern appears in display code.

## Display

`xz_display_options(void *buffer, int size)` validates and prints stored compressor options:

- Dictionary size.
- Selected filter list, or “No filters specified”.

It expects exactly `sizeof(struct comp_opts)` and reports a stored-option read error on invalid size or invalid dictionary encoding.

## Initialization

`xz_init(void **strm, int block_size, int datablock)` allocates:

- `struct xz_stream`
- an array of `struct filter` entries

For metadata blocks, only one plain LZMA2 filter chain is used and dictionary size is `SQUASHFS_METADATA_SIZE`.

For data blocks, the stream uses `dictionary_size` and creates one candidate for plain LZMA2 plus one candidate for each selected BCJ filter. BCJ candidates receive their own temporary `block_size` output buffer; the plain candidate writes directly to the destination buffer.

The function uses `MALLOC`, so allocation failure behavior is delegated to the Squashfs allocation helper.

## Compression

`xz_compress()` tries each configured filter chain and selects the shortest successful compressed output.

Per candidate:

1. Initialize `stream->opt` from `lzma_lzma_preset(&stream->opt, preset)`.
2. Set `stream->opt.dict_size`.
3. Apply BCJ-specific LZMA tuning:
   - ARMTHUMB/RISCV: `lp = 1`.
   - POWERPC/ARM/SPARC/ARM64: `lp = 2`, `lc = 2`.
   - IA64: `pb = 4`, `lp = 4`, `lc = 0`.
4. Apply explicit user overrides `lc`, `lp`, `pb` if set.
5. Call `lzma_stream_buffer_encode()` with `LZMA_CHECK_CRC32`.

If a candidate succeeds, it can become the selected shortest output. `LZMA_BUF_ERROR` is treated as output-buffer overflow for that candidate and is not fatal. Other liblzma errors fail the whole compression call and return `-1` with `*error` set.

If no candidate fits in the destination buffer, the function returns `0`, matching the Squashfs compressor convention for “not enough output space”. If the selected candidate used a temporary BCJ buffer, the compressed data is copied back to `dest`.

## Decompression

`xz_uncompress()` calls `lzma_stream_buffer_decode()` with `MEMLIMIT`, checks that liblzma returned `LZMA_OK`, and also verifies all input bytes were consumed. On success it returns decompressed byte count. On failure it returns `-1` and stores the liblzma result code in `*error`.

## Usage and Option Arity

`xz_usage()` prints help text for all supported `-X` options. `option_args()` tells the generic option parser that all XZ options except `-Xe` consume one argument.

## Registered Compressor

`xz_comp_ops` registers:

- `.id = XZ_COMPRESSION`
- `.name = "xz"`
- `.supported = 1`

and supplies init, compress, uncompress, option parsing, post-processing, dump/extract/display, usage, and option-arity callbacks.

## Research Notes

This file is the extended XZ policy layer for Squashfs tools. Its most important behavior is that data block compression can evaluate several candidate filter chains and choose the smallest result, while metadata compression remains plain LZMA2 with metadata dictionary size. Stored filesystem options preserve dictionary size and BCJ filter choices for append compatibility, but do not preserve every extended tuning knob.
