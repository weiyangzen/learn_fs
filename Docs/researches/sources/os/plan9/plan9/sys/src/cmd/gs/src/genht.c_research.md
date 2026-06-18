# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/genht.c

Read status: complete.

Purpose: build-time generator that compiles constrained PostScript halftone resource files into C data structures for Ghostscript ROM/shared read-only use.

Input format:
- Parses a restricted PostScript-like resource syntax.
- Supports `HalftoneType 5` as a prefix/resource grouping marker.
- Supports `HalftoneType 3` resources with `Width`, `Height`, and `Thresholds`.
- Decodes ASCII hex threshold data.

Main logic:
- `read_file` loads the entire resource file.
- `parse_line` trims whitespace and returns one logical line at a time.
- `parse_halftone` scans for resource names and halftone parameters, validates width/height, allocates level/bit arrays, and decodes thresholds via `s_AXD_template`.
- `write_halftone` emits static C arrays for levels and bit data plus a `gx_device_halftone_resource_t`.
- `main` writes generated C comments/includes, constructs threshold orders with `ht_order_procs_short.construct_order`, emits all resources, and writes a `gs_dht_<prefix>` accessor procedure.

Dependencies:
- Includes halftone/device headers and stream/string internals.
- Includes `gxhtbit.c`, `scantab.c`, and `sstring.c` directly to avoid a separate link step.
- Provides minimal stubs for Ghostscript structure relocation/enumeration and threshold completion.

Filesystem/storage relevance:
- Reads a halftone resource file and writes generated C.
- No runtime storage behavior.

Notable behavior and risks:
- Assumes small/simple input grammar.
- Width and height are capped at `0x4000`, but `Width * Height` is held in `uint`/`int` style variables.
- Allocations are not comprehensively freed because the process is a short-lived generator.
