# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7500, source bytes 262126, report `Docs/researches/chunks/chunk_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevupd_c_1_1_7500_04212c3af4f5_research.md`
- chunk 2: lines 7501-7642, source bytes 2898, report `Docs/researches/chunks/chunk_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevupd_c_2_7501_7642_724fcc7e6725_research.md`

## Chunk Research

### Chunk 1: lines 1-7500

# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c lines 1-7500

## Scope

This chunk covers nearly all of Ghostscript's old `uniprint` printer driver implementation in 9front's imported `cmd/gs` tree. The source tree `sources/os/plan9/9front` is included by `Docs/research_subset_a.md`; this file is not filesystem code, but it is in the scoped Plan 9 source tree. Lines 1-7500 define the device prototype, parameter tables, private driver state, device lifecycle, Ghostscript parameter import/export, color mapping, Floyd-Steinberg rendering, output-buffer setup, Sun raster/ESC/P/ESC/P2/nozzle-map/PCL/Canon writers, run-length compression, and forward plus reverse pixel-reader dispatch setup. The chunk ends just before the reverse pixel-reader function bodies continue at line 7501.

## APIs and Entry Points

- The exported driver object is `gs_uniprint_device`, a `upd_device` built with `prn_device_body()` and the private procedure table `upd_procs`.
- Ghostscript device callbacks implemented here are `upd_open()`, `upd_close()`, `upd_print_page()`, `upd_get_params()`, `upd_put_params()`, color encode/decode callbacks, and CMYK mapping callbacks.
- Color mapping callbacks include grayscale, RGB, RGBW/white-generation, CMYK/KCMY, generated-black CMYK, RGB-to-CMYK with UCR for overprint, and RGB-to-CMY_K modes.
- Internal setup/teardown APIs are `upd_open_map()`/`upd_close_map()`, `upd_open_render()`/`upd_close_render()`, `upd_open_writer()`/`upd_close_writer()`, and writer-specific open/start/write routines.
- Rendering functions selected by `upRendering` are `upd_fscomp()`, `upd_fscmyk()`, and `upd_fscmy_k()`.
- Output writers selected by `upOutputFormat` are Sun raster (`upd_rascomp()`), ESC/P (`upd_wrtescp()`), ESC/P2 Y-weave (`upd_wrtescp2()`), ESC/P2 X/Y-weave (`upd_wrtescp2x()`), Epson nozzle-map (`upd_wrtescnm()`), HP RTL/PCL (`upd_wrtrtl()`), and Canon extended mode (`upd_wrtcanon()`).
- Pixel-reader entry setup is `upd_pxlfwd()` and `upd_pxlrev()`, which install specialized `upd_pxlget*` callbacks for packed depths 1/2/4/8/16/24/32 bits. Reverse reader bodies are a cross-chunk continuation.

## Parameter Surface

The driver exposes a large `up*` parameter namespace through `upd_get_params()` and `upd_put_params()`. Choice parameters are `upColorModel`, `upRendering`, and `upOutputFormat`. Boolean flags control FS direction/whitespace/random init, begin-page command rewriting, absolute X/Y positioning, initialized-state reporting, abort/error/open state, Y-flip, and black reduction.

Integer parameters define output dimensions/components, scan-buffer count, X/Y step and offsets, pins, weave pass counts, begin/end weave regions, weave scan offset, and nozzle-map rows/pattern repeat. Integer arrays define Ghostscript `color_info`, component bit widths/shifts/order, normal/initial/final weave feeds and X starts, initial/final pin masks, nozzle row masks, and nozzle scan offsets. String and string-array parameters hold job/page begin/end/abort commands, movement commands, component-selection commands, and component-write commands. Float arrays define transfer curves, margins, and an unused/visible color-map slot.

## Core Control Flow

`upd_put_params()` is the configuration ingress. It reads all supported parameters from a Ghostscript `gs_param_list`, accepts null as reset-to-empty, copies incoming arrays/strings into driver-owned memory, derives missing `upColorInfo`, component bit widths, component shifts, gray/color ramp values, and margins, then calls `gdev_prn_put_params()`. If meaningful parameters or geometry changed while the device is open, it closes the device so later `upd_open()` recomputes map/render/writer state.

`upd_open()` optionally enforces `upMargins`, calls `gdev_prn_open()`, clears print-ready bits, initializes color mapping, computes printable Ghostscript raster width/height after margins, allocates one raw `gsbuf` scanline, opens rendering, opens the selected writer, and records opened device geometry. The print loop is allowed only when `B_MAP|B_BUF|B_RENDER|B_FORMAT` are set and `B_ERROR` is clear.

`upd_print_page()` writes job-open and page-begin sequences, initializes page-local counters, calls optional render/writer start hooks, then repeatedly pulls scanlines with `get_bits`, renders them into circular component scan buffers, and calls the selected writer while enough rendered lines are buffered for the current weave/pass geometry. It handles signal-triggered aborts when `UPD_SIGNAL` is enabled, emits an abort sequence if configured, otherwise emits the page-end sequence, and emits the close sequence for one-page-per-file output patterns.

`upd_close()` writes any deferred job-close sequence, closes writer/render/map state, frees the driver-owned parameter copies and `upd` object, then calls `gdev_prn_close()`.

## Color Mapping

`upd_open_map()` maps the selected color model to component transfer curves, validates component bit counts and shifts against Ghostscript depth, supplies default two-point transfer curves, requires monotonic transfer curves, allocates per-component expansion tables, interpolates transfer data into `gx_color_value` code tables, stores component metadata in `upd->cmap[]`, sets `upd->ncomp`, and installs the matching Ghostscript procedure callbacks through `upd_procs_map()`.

`upd_truncate()` maps a full-range `gx_color_value` to packed component bits using a binary search over the interpolated transfer table and inverts falling transfer curves. `upd_expand()` reverses this from a packed `gx_color_index`.

The mapping functions use a few format-specific tricks. RGBW and CMYK grayscale cases encode gray only through the white/black component to avoid generating `gx_no_color_index`; multi-component encoders flip bit 0 if truncation would produce the reserved no-color value. `MAP_CMYKGEN` generates black as the minimum of CMY except for plain K-only input. `MAP_RGBOV` performs CMYK black generation plus undercolor removal using `(CMY-K)/(1-K)`, while `MAP_RGBNOV` subtracts generated black directly from CMY for CMY plus K printing.

## Rendering and Scan Buffers

Rendering converts Ghostscript packed color indices into one-bit-per-component scan buffers. `upd_open_render()` computes `rwidth` from the Ghostscript width and optional output width, then dispatches to the configured rendering setup.

`upd_open_fscomp()` validates component order, allocates one `updcomp_t` per component and a shared `valbuf` sized as `(rwidth + 2) * ncomp`, computes FS offset/scale/threshold/spotsize from component transfer curves, optionally randomizes the error buffer unless `upFSZeroInit` is set, and installs `upd_fscomp()`. `upd_fscomp()` supports 1/3/4 component output, optional alternating or fixed direction, optional whitespace skipping, Y-flip, and optional K reduction that replaces multi-color dot combinations with black when configured. It updates per-pass `xbegin`/`xend` limits when the writer needs X-weave bounds.

`upd_open_fscmyk()` builds on component FS but only accepts four components with 8-bit channels in 32-bit KCMY byte order, then installs `upd_fscmyk()`. That renderer reads 32-bit scan data directly, computes black first, restricts color firing when black dominates, and distributes FS error in K/CMY-aware order. `upd_open_fscmy_k()` requires four components and installs `upd_fscmy_k()`, which chooses either black or CMY firing to support CMY/K-separated output.

## Writer Setup and Output Formats

`upd_open_writer()` depends on successful rendering. It normalizes pass and pin counts, creates default weave feeds/X starts when absent, validates begin/end weave arrays and component command arrays, computes a power-of-two circular scan-buffer count, computes `pwidth`, `pheight`, `nbytes`, and `scnmsk`, calls the selected writer-specific open function, allocates `outbuf`, then allocates `scnbuf[scan][component]` byte arrays and optional pass-limit arrays.

`upd_limits()` scans rendered component bytes to compute pass-specific first/last printable X positions for writers with X-weaving. Sun raster output writes an optional raster header in `upd_start_rascomp()` and emits either one-bit grayscale or packed component indices per scanline in `upd_rascomp()`.

The ESC/P writer validates movement/write commands, can patch page length inside ESC/P begin-page commands, calculates worst-case command/data buffer size, and writes pin-pass data in `upd_wrtescp()`. It positions Y and X, selects components, writes printer raster commands, packs vertical pin columns, emits each component, and advances through initial/normal/final weave feed tables.

The ESC/P2 setup parses and optionally rewrites begin-page resolution/page-length/top/bottom-margin commands, synthesizes Y-move and sometimes X-move/X-step commands, initializes nozzle-map defaults, synthesizes default component selection and write commands, and dispatches to Y-only, X/Y, or nozzle-map writers. `upd_wrtescp2()` writes RLE-compressed byte rows for Y-weave output. `upd_wrtescp2x()` repacks X-weaved pixels into a temporary front region of `outbuf`, RLE-compresses them, and writes compressed rows. `upd_wrtescnm()` is a Stylus Color 300-oriented variant that emits a fixed component-selection path and uses row-mask/scan-offset arrays to map output rows to component scanlines.

`upd_rle()` implements the common PackBits-like compressor used by ESC/P2, PCL/RTL, Canon, and blank-row fill. `upd_open_wrtrtl()` rewrites HP PCL and PJL begin-page commands for width, length, and resolution using a large byte-state parser, validates component write commands, and sizes output buffers. `upd_wrtrtl()` emits optional vertical movement and one compressed row per component. `upd_open_wrtcanon()` only sizes the line buffer and installs `upd_wrtcanon()`, which writes Canon extended-mode vertical movement and one compressed row per component with component letters `K` or `YMCK`.

## State and Dependencies

The central `upd_s` object owns parameter copies, `cmap[]`, the raw Ghostscript scan buffer, current pixel-reader state, render and writer function pointers, circular component scan buffers, FS error buffers, writer output buffer, readiness/error flags, opened geometry, printable dimensions, component counts, buffer sizes, pass/cursor state, selected component/linefeed state, and printer/scan positions.

This chunk depends on Ghostscript printer-device APIs from `gdevprn.h`, parameter APIs from `gsparam.h`, Ghostscript memory allocation (`gs_malloc`/`gs_free`), color and device procedure conventions, C stdlib/limits/ctype helpers, optional POSIX signals, `FILE *` I/O, architecture endian/word-size macros, and Ghostscript macros such as `countof`, `set_dev_proc`, `dev_proc`, margin helpers, and `gx_device_raster()`.

## Risks and Edge Cases

- The driver mutates configured begin-page command byte strings in place after copying them; malformed or short command strings can evade intended rewriting or produce surprising printer commands.
- Output buffer sizing is manual and shared with many `memcpy`, `sprintf`, `fprintf`, `fwrite`, and RLE paths. Any mismatch between sizing estimates and generated command/data bytes risks overflow.
- `upd_put_params()` uses `error` both as an error code and a change bitset. This works only while all change bits remain positive and all real errors remain negative.
- Several geometry and pass calculations multiply user-controlled parameters before later bounds checks; large widths, heights, pass counts, or pin counts can overflow intermediate signed integers.
- `upd_pxlrev()` computes `width-1` as unsigned. If an invalid configuration yields zero width, reverse setup underflows.
- `upd_truncate()` assumes allocated transfer code tables have sentinel/neighbor entries compatible with `p[-1]` access during search; malformed bit counts or table construction bugs would be memory-sensitive.
- Debug-only code in `upd_1color_rgb()` references `prgb[0]` even though the function parameter is `cv`, so enabling `UPD_M_MAPCALLS` appears to expose a compile-time bug.
- The `UPD_M_FSBUF` initialization loop in `upd_open_fscomp()` uses `UPD_VALPTR_MAX < icomp`, which never initializes the arrays as intended.
- `upd_close_writer()` frees `bytes` using `sizeof(...words[0])`, but `updscan_t` in this chunk has a `bytes` member and no `words` member, indicating either a stale local edit or a compile-time break in this 9front copy.
- Signal abort state is stored in a single static `sigupd`, so concurrent print jobs would not be signal-safe.

## Cross-Chunk References

- Lines 7501-7642 continue the reverse pixel-reader bodies (`upd_pxlget1r*`, `2r*`, `4r*`, `8r`, `16r`, `24r`, `32r`). The renderers in this chunk call `upd_pxlrev()` and then repeatedly invoke the installed reverse callback, so the tail chunk completes a required runtime path.
- The final per-file report must merge this chunk with the tail to cover all pixel-reader behavior and any file-ending macros or cleanup.
- External Ghostscript `.upp` configuration files are expected to provide the `up*` parameters consumed here; this chunk only defines the driver-side parameter contract.

### Chunk 2: lines 7501-7642

# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c lines 7501-7642

## Scope

This report covers only `sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c` lines 7501-7642 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context to identify the reverse-pixel setup routine, the `upd_pxlget` function-pointer API, and the rendering/compression consumers. The chunk is Ghostscript UPD printer-driver pixel-reader code embedded in 9front's vendored `gs` tree.

## APIs

The chunk defines private `uint32_t name(upd_p upd)` pixel getter routines selected through `upd->pxlget` and invoked via the `upd_pxlget(UPD)` macro:

- `upd_pxlget1r1` through `upd_pxlget1r8`: reverse readers for 1-bit pixels packed most-significant-bit first in each source byte. Each function returns `0` or `1`, then rewires `upd->pxlget` to the previous bit-position function for the next pixel.
- `upd_pxlget2r1` through `upd_pxlget2r4`: reverse readers for 2-bit packed pixels. They mask and shift `0xC0`, `0x30`, `0x0C`, or `0x03` and rotate the function pointer backward through the four pixel slots.
- `upd_pxlget4r1` and `upd_pxlget4r2`: reverse readers for 4-bit packed pixels. They return the high or low nibble and toggle the getter state between the two nibbles.
- `upd_pxlget8r`, `upd_pxlget16r`, `upd_pxlget24r`, `upd_pxlget32r`: reverse readers for byte-aligned 8/16/24/32-bit pixels. They assemble a `uint32_t` from `upd->pxlptr` while walking the byte pointer backward.

All routines depend on the local `upd_proc_pxlget` signature macro and mutate fields of `struct upd_s`: `byte *pxlptr` and `uint32_t (*pxlget)(upd_p)`.

## Control Flow

The control flow is a hand-written finite-state machine encoded as self-modifying function-pointer state:

- For sub-byte depths, each call both returns the current packed pixel and installs the getter for the next reverse pixel position.
- The decrement of `upd->pxlptr` happens only when crossing a source-byte boundary: `upd_pxlget1r1`, `upd_pxlget2r1`, and `upd_pxlget4r1` consume the high-order slot and then move to the preceding byte. The remaining sub-byte functions inspect the current byte without moving the pointer.
- For 8-bit and wider depths, every pixel is byte-aligned, so each function decrements `pxlptr` for every source byte consumed.
- Multi-byte reverse readers assemble the returned integer little-endian relative to the backward walk: the byte at the current pointer becomes the low-order byte, then earlier addresses are shifted by 8, 16, and 24 bits.

Adjacent setup in `upd_pxlrev` positions `upd->pxlptr` at the last printable/source pixel and selects the correct initial function based on `IA_COLOR_INFO.data[1]` depth and bit offset. Consumers in the Floyd-Steinberg render paths call `upd_pxlget(upd)` repeatedly while trimming whitespace and processing pixels.

## State And Dependencies

This chunk has no global storage of its own, no allocation, no I/O, and no external library calls. Its runtime state is entirely carried in the mutable `upd` object:

- `upd->pxlptr` must already point into `upd->gsscan` at the byte and byte-offset chosen for a reverse scan.
- `upd->pxlget` is both the dispatch target and the continuation state for the next pixel.
- `upd->int_a[IA_COLOR_INFO].data[1]`, `upd->pwidth`, `upd->gswidth`, and `upd->gsscan` are consumed by the adjacent initializer, not directly by this chunk.

The chunk depends on C integer promotion behavior for `byte` values, explicit casts to `uint32_t` before multi-byte shifts, and the invariant that caller-visible scan widths keep `pxlptr` within the raster buffer while walking backward.

## Risks

Pointer safety is the main risk. None of these getters check bounds or null pointers; `upd_pxlrev` handles a null `gsscan`, but after initialization the render loops assume the selected width and source buffer are consistent. An off-by-one in width, depth, or initial offset would under-read before `gsscan`.

The sub-byte readers are fragile because pointer movement is tied to specific state functions. Changing the state transitions or moving the `pxlptr--` to the wrong function would duplicate or skip packed pixels. This also affects whitespace-trimming code that snapshots both `upd->pxlget` and `upd->pxlptr` to roll back to the last non-white position.

The 16/24/32-bit reverse readers intentionally return a value with the rightmost scanned byte in the low-order bits. Any caller or future maintainer expecting the same byte order as the forward readers would misinterpret color component extraction.

## Cross-Chunk References

The previous chunk contains the declarations for these functions, the forward pixel readers, `upd_pxlgetnix`, and `upd_pxlrev`. In particular, lines 7437-7499 initialize this chunk's reverse-reader state machine by computing the initial byte/bit offset and, for 16/24/32-bit depths, advancing `pxlptr` to the last byte of the pixel before the first reverse read.

Earlier render/compression code around `upd_fscomp` and its 4-component variant uses `upd_pxlfwd`, `upd_pxlrev`, and `upd_pxlget` to trim leading/trailing white pixels and then read one source pixel per output step. Later chunks are not needed for this chunk's local behavior; this section ends at `upd_pxlget32r`.
