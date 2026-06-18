# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevupd.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7500, source bytes 262126, report `Docs/researches/chunks/chunk_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevupd_c_1_1_7500_b9d052209f12_research.md`
- chunk 2: lines 7501-7642, source bytes 2898, report `Docs/researches/chunks/chunk_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevupd_c_2_7501_7642_4fac1f096e10_research.md`

## Chunk Research

### Chunk 1: lines 1-7500

# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevupd.c lines 1-7500

## Scope

This chunk covers the Ghostscript `uniprint` printer driver from file start through the forward pixel readers and reverse-reader dispatcher. The final reverse pixel reader implementations continue after this chunk at lines 7501-7642.

## High-Level Role

`gdevupd.c` implements Ghostscript's `uniprint` device, a configurable raster printer driver driven by PostScript-visible parameters. It maps Ghostscript color values to packed device pixels, dithers scanlines into per-component 1-bit output planes, and writes those planes in several printer command formats: Sun raster, ESC/P, ESC/P2, HP RTL/PCL, Canon extended mode, and Epson nozzle-map mode.

The exported device object is `gs_uniprint_device`, built on `gx_device_common`, `gx_prn_device_common`, and a custom `upd` extension pointer. The device procedure table installs custom open, close, print-page, get-params, put-params, and color mapping behavior.

## Public / Device-Facing APIs

- `upd_print_page(gx_device_printer *pdev, FILE *out)`: main page renderer/writer. It requires `B_OK4GO` (`B_MAP | B_BUF | B_RENDER | B_FORMAT`) and writes job/page open/close/abort command strings around the scan conversion loop.
- `upd_open(gx_device *pdev)`: calls `gdev_prn_open`, applies `upMargins`, opens color mapping, allocates the Ghostscript scanline buffer, opens rendering, and opens the writer.
- `upd_close(gx_device *pdev)`: emits pending close command if a job is open, frees writer/render/map/parameter memory, then calls `gdev_prn_close`.
- `upd_get_params(...)`: exports `upVersion` plus all named choices, flags, ints, int arrays, strings, string arrays, and float arrays.
- `upd_put_params(...)`: imports the same parameter families, copies/mutates them off to the side, adjusts `color_info`, margins, and geometry, closes the device on meaningful changes, installs new `upd` state, and refreshes color procedures.
- Color map procedures selected by `upd_procs_map`: grayscale, RGB, RGBW, CMYK/KCMY, generated black, and RGB-to-CMYK variants.

## Parameter Model and State

The central state is `struct upd_s`. It owns:

- Parameter arrays: `choice`, `ints`, `int_a`, `strings`, `string_a`, `float_a`.
- Color maps: four `updcmap_t` entries with code tables, masks, shifts, transfer curve index, component output order, and monotonic direction.
- Input raster: `gsbuf`, `gsscan`, `pxlptr`, and `pxlget`.
- Rendering: `render`, `start_render`, `valbuf`, `valptr`.
- Output: `writer`, `start_writer`, ring `scnbuf`, `outbuf`, dimensions, pass counters, printer positions, and flags.

Configuration is exposed as PostScript/Ghostscript parameters:

- Choices: `upColorModel`, `upRendering`, `upOutputFormat`.
- Flags: FS direction/white/zero options, page command adjustment flags, absolute positioning, initialized-state flags, abort/error/open flags, Y flip, and K reduction.
- Ints: output size/components, scan buffers, X/Y step and offset, pin/pass/weave geometry, nozzle-map row/repeat parameters.
- Int arrays: `upColorInfo`, component bits/shifts/order, weave feed/start/pin tables, nozzle row mask and scan offsets.
- Strings: model, begin/end job/page, abort, X/Y movement, step, and linefeed commands.
- String arrays: component-select and component-write commands.
- Float arrays: transfer curves for W/R/G/B/K/C/M/Y plus margins and color map.

Memory management is macro-based (`UPD_MM_*`) around `gs_malloc`/`gs_free`, because parameters are copied into mutable driver-owned storage.

## Control Flow

Open/setup flow:

1. `upd_put_params` reads requested parameters, computes defaults for `upColorInfo`, `upComponentBits`, and `upComponentShift`, updates Ghostscript `color_info`, and closes the device if live state must be rebuilt.
2. `upd_open` applies private margins, calls superclass open, invokes `upd_open_map`, allocates `gsbuf`, invokes `upd_open_render`, invokes `upd_open_writer`, and records opened geometry.
3. `upd_open_map` validates mapper choice, bit widths/shifts, monotonic transfer curves, allocates color code tables, fills inverse mapping tables, sets `ncomp`, and installs device color procedures.
4. `upd_open_render` selects one rendering algorithm and initializes `valbuf` / `valptr`.
5. `upd_open_writer` normalizes pass/weave defaults, validates arrays and command strings, computes ring buffer sizes, asks the format-specific open routine for output needs, and allocates `outbuf` plus per-component scan buffers.

Print flow:

1. `upd_print_page` emits job open once and page begin every page, resets page counters, and calls optional start hooks.
2. It repeatedly fills the scan ring by calling Ghostscript `get_bits` into `gsbuf` (or zero-fill past source height), then calling `upd->render`.
3. It writes buffered output while enough scanlines are available for the current weave/pin window by calling `upd->writer`.
4. It handles interrupt aborts via `B_ABORT`, emits abort or page-end command, optionally closes one-page-per-file jobs, flushes, and returns interrupt/I/O/success status.

Close flow frees buffers in reverse setup order and removes installed color map state.

## Color Mapping

`upd_truncate` maps a full `gx_color_value` into a component code using a monotonic transfer table and component mask/shift. `upd_expand` reverses packed component bits into a `gx_color_value`.

The color models are:

- `MAP_GRAY`: `upd_rgb_1color` / `upd_1color_rgb`.
- `MAP_RGB`: packed component-wise RGB.
- `MAP_RGBW`: RGB plus a white component; grayscale is represented through W only.
- `MAP_CMYK`: KCMY packing, with grayscale optimized through K.
- `MAP_CMYKGEN`: CMY input with generated K based on minimum CMY.
- `MAP_RGBOV`: RGB-to-KCMY with black generation and undercolor removal using normalized `(CMY-K)/(1-K)`.
- `MAP_RGBNOV`: RGB-to-KCMY with black generation and simple `CMY-K`.

Several mappers avoid returning `gx_no_color_index` by flipping the low bit if truncation produces the sentinel value.

## Rendering

Rendering converts packed Ghostscript pixels into component bitplanes in `scnbuf`.

- `upd_open_fscomp` builds `updcomp_t` entries according to optional component order, allocates error buffers sized `(2 + rwidth) * ncomp`, computes threshold/spotsize/scale/offset from transfer curves, and optionally randomizes error initialization unless `B_FSZERO` is set.
- `upd_fscomp` is the general component-wise Floyd-Steinberg renderer. It supports forward/reverse scan direction, optional alternating direction (`B_FIXDIR` disables toggling), Y flip, whitespace trimming unless `B_FSWHITE`, and optional black reduction (`B_REDUCEK`).
- `upd_open_fscmyk` reuses FS setup but only enables optimized `upd_fscmyk` for 4-component, byte-aligned KCMY depth/shift layout.
- `upd_fscmyk` directly reads 32-bit KCMY-style scan data and applies specialized black/color firing rules.
- `upd_open_fscmy_k` enables `upd_fscmy_k` for four components; `upd_fscmy_k` prefers black when possible and otherwise fires color components.
- `upd_limits` computes per-X-pass first/last set pixels for writers that need sparse range emission.

## Writers and Output Formats

`upd_open_writer` dispatches to format open routines:

- `FMT_RAS`: `upd_open_rascomp`, `upd_start_rascomp`, `upd_rascomp`. Writes uncompressed Sun raster headers/data. Multicomponent output is assembled into indexed bytes with a generated color map.
- `FMT_EPSON`: `upd_open_wrtescp`, `upd_wrtescp`. Writes ESC/P `ESC *`-style pin data with X/Y weaving, component selection, movement commands, and linefeed fallback.
- `FMT_ESCP2Y`: `upd_open_wrtescp2`, `upd_wrtescp2`. Writes ESC/P2 compressed vertical pass data, no multiple X passes.
- `FMT_ESCP2XY`: `upd_wrtescp2x`. Adds X weaving by repacking selected X-pass pixels into temporary output bytes before RLE.
- `FMT_ESCNMY`: `upd_wrtescnm`. Epson Stylus Color 300 nozzle-map variant using `I_ROWS`, `I_PATRPT`, `IA_ROWMASK`, and `IA_SCNOFS` to expand logical component rows into nozzle-map output rows.
- `FMT_RTL`: `upd_open_wrtrtl`, `upd_wrtrtl`. Parses and optionally rewrites PCL/RTL/PJL begin-page strings for page width/length/resolution, then writes RLE-compressed component scanlines.
- `FMT_CANON`: `upd_open_wrtcanon`, `upd_wrtcanon`. Writes Canon extended mode commands, compressed scanline payloads, and vertical advances.

`upd_rle` implements PackBits-like run-length encoding and also emits compressed zero rows when input is `NULL`.

## Pixel Readers

The chunk includes declarations for all pixel readers, full forward readers, the dummy reader, and the reverse-reader dispatcher:

- `upd_pxlfwd` selects a forward reader for 1/2/4/8/16/24/32-bit depths and points `pxlptr` at `gsscan`.
- Forward readers are state-machine functions that update `upd->pxlget` for sub-byte depths and advance `pxlptr` at byte boundaries.
- `upd_pxlrev` computes the starting pointer at the last in-range pixel and selects a reverse reader based on depth and bit offset.
- Reverse reader implementations themselves start at line 7501, outside this chunk.

## Dependencies

Internal Ghostscript dependencies visible here include:

- Device and printer APIs: `gx_device`, `gx_device_printer`, `gx_device_procs`, `gdev_prn_open`, `gdev_prn_close`, `gdev_prn_get_params`, `gdev_prn_put_params`, `gdev_prn_output_page`, `gx_device_raster`, `gx_device_set_margins`, `dev_proc`, `set_dev_proc`.
- Parameter APIs: `gs_param_list`, `gs_param_string`, `gs_param_*_array`, `param_read_*`, `param_write_*`, `param_signal_error`.
- Color/device constants and helpers: `gx_color_value`, `gx_color_index`, `gx_max_color_value`, `gx_no_color_index`, `gx_default_map_*`, `color_info`.
- Memory and error APIs: `gs_malloc`, `gs_free`, `return_error`, `gs_error_VMerror`, `gs_error_interrupt`, `gs_error_ioerror`, `gs_error_undefined`.
- Standard C/runtime: `FILE`, `fwrite`, `fprintf`, `fputc`, `fflush`, `ferror`, `memcpy`, `memset`, `strlen`, `strncmp`, `strchr`, `sprintf`, `rand`, `signal`.

## Risks and Edge Cases

- The file mutates command strings imported as parameters; all strings are copied into mutable storage, but this makes ownership and lifetime correctness depend on the `UPD_MM_*` macros.
- `upd_put_params` uses `error` as both a negative error code and a positive bitfield of changed parameter groups. This is fragile and requires strict sign checks.
- Several writer paths compute output buffer sizes manually and then assemble data with raw pointer arithmetic. Invalid weave/pin/step parameters could cause underestimation if validation misses a case.
- `upd_open_map` only warns on overlapping component bit fields under `UPD_M_WARNING`; overlap is not made fatal unless other validation fails.
- Transfer curves must be monotonic. Invalid curves disable mapping; default two-point transfer curves are synthesized when missing.
- `upd_truncate` relies on code tables and binary-search-like indexing around `p[-1]`; correctness depends on allocated table shape and monotonic fill.
- `upd_print_page` ignores writer return values; it detects final errors only through abort state, scan progress, and `ferror`.
- Signal handling uses a single static `sigupd`, so concurrent devices or nested signal-sensitive operations would not be safe.
- `upd_close_writer` references `upd->scnbuf[ibuf][icomp].words[0]`, but `updscan_t` in this chunk has only `bytes`, `xbegin`, and `xend`; this appears inconsistent in the visible source.
- The `UPD_MESSAGES & UPD_M_MAPCALLS` block in `upd_1color_rgb` refers to `prgb[0]`, but the function parameter is named `cv`; this looks like a conditional compilation bug.
- `upd_open_fscomp` debug initialization loop is written `for(icomp = 0; UPD_VALPTR_MAX < icomp; ++icomp)`, which never runs; only affects `UPD_M_FSBUF` diagnostics.
- Nozzle-map code contains comments expressing uncertainty and manually manipulates `y` inside the loop; this path has higher risk of off-by-one scan selection.
- Final reverse pixel reader functions are outside this chunk, so reverse rendering behavior is only partially visible here.

## Cross-Chunk References

- Lines 7501-7642 continue the reverse pixel readers selected by `upd_pxlrev` in this chunk: `upd_pxlget1r*`, `upd_pxlget2r*`, `upd_pxlget4r*`, `upd_pxlget8r`, `upd_pxlget16r`, `upd_pxlget24r`, and `upd_pxlget32r`.
- There is no later per-file logic after the pixel readers; the next chunk should mainly validate reverse reader pointer movement and end-of-file closure.

### Chunk 2: lines 7501-7642

# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevupd.c lines 7501-7642

## Scope

This chunk is the reverse-direction half of Ghostscript `upd` pixel-reader helpers in Plan 9's vendored `gs` tree, within `Docs/research_subset_a.md` Plan 9 OS source scope. It defines private `uint32_t` readers for 1, 2, 4, 8, 16, 24, and 32 bits per source pixel when the raster stream is consumed right-to-left/backward.

## APIs and Entry Points

- `upd_pxlget1r1()` through `upd_pxlget1r8()` read one 1-bit pixel from bit masks `0x80` through `0x01`, returning `0` or `1`.
- `upd_pxlget2r1()` through `upd_pxlget2r4()` read one 2-bit pixel from masks `0xC0`, `0x30`, `0x0C`, and `0x03`, returning the field shifted to bit 0 where needed.
- `upd_pxlget4r1()` and `upd_pxlget4r2()` read high and low nibbles.
- `upd_pxlget8r()`, `upd_pxlget16r()`, `upd_pxlget24r()`, and `upd_pxlget32r()` read whole-byte pixels and combine multibyte color indexes into `uint32_t`.
- These helpers are called indirectly through `upd_pxlget(UPD)`, which expands to the `upd->pxlget` function pointer.

## Control Flow

Each sub-byte reader is a tiny state machine: it returns the current bit field and rewrites `upd->pxlget` to the helper that should read the next pixel position. In reverse mode, the first sub-byte helper for a byte decrements `upd->pxlptr` after reading that byte, then later helpers continue using the decremented pointer until the cycle wraps to the next previous byte.

For 1-bit pixels, the cycle moves `1r8 -> 1r7 -> ... -> 1r1 -> 1r8`, with `1r1` consuming the high bit and post-decrementing the byte pointer. For 2-bit pixels, `2r4 -> 2r3 -> 2r2 -> 2r1 -> 2r4`, with `2r1` post-decrementing. For 4-bit pixels, `4r2 -> 4r1 -> 4r2`, with `4r1` post-decrementing.

Whole-byte readers do not change `upd->pxlget`; they only step `upd->pxlptr` backward by the pixel width. Multibyte reverse readers assemble values little-endian from the reverse traversal point: 16-bit reads current byte as low 8 bits and previous byte as high 8 bits, 24-bit reads low/mid/high bytes, and 32-bit reads four bytes into bits 0, 8, 16, and 24.

## State, Dependencies, Risks

State touched is limited to `upd->pxlptr` and, for sub-byte formats, `upd->pxlget`. Both fields live in `struct upd_s`; `pxlptr` is the current source cursor and `pxlget` is the active pixel-reader callback.

The immediate dependency is `upd_pxlrev()` immediately before this chunk, which initializes `upd->pxlptr` from `upd->gsscan`, positions it at the last pixel for the active width/depth, and selects the correct reverse helper based on `IA_COLOR_INFO.data[1]`. Earlier prototypes declare all helpers through `upd_proc_pxlget(name)`, and rendering paths call them through `upd_pxlget(upd)` while scanning or trimming white pixels.

The main risks are pointer-boundary correctness and state-machine alignment. These helpers assume `upd_pxlrev()` has selected an entry function matching the ending bit offset and that callers will not read past the beginning of `gsscan`. A bad depth, width, or offset would make the post-decrement operations underflow the source scanline. Because the function pointer is mutated on every sub-byte read, any caller that snapshots/restores `upd->pxlget` must also keep `upd->pxlptr` synchronized; nearby render code does this while skipping leading whitespace.

## Cross-Chunk References

- Lines 7207-7253 contain the private prototypes for all forward and reverse pixel readers.
- Lines 7255-7424 define the forward-direction setup and forward pixel readers mirrored by this chunk.
- Lines 7432-7499 define the dummy reader and `upd_pxlrev()`, which dispatches into this chunk.
- Lines 3608-3692 and 3998-4075 show render paths selecting forward/reverse readers, trimming whitespace, restoring `pxlget`/`pxlptr`, and consuming pixels through `upd_pxlget(upd)`.
