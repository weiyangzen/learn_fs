# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfm.c

This file writes Ghostscript CMap objects in standard PostScript resource format. It serializes code space ranges, CID mappings, notdef mappings, bfchar/bfrange mappings, font-index switches, and CIDSystemInfo dictionaries.

Key helpers:
- `pput_string_entry` writes a `gs_const_string` with a literal prefix.
- `pput_hex` emits bytes as lowercase hexadecimal.
- `cmap_put_ranges` emits `begincodespacerange` blocks.
- `cmap_put_system_info` emits either `null` or a `Registry`/`Ordering`/`Supplement` dictionary.
- `cmap_put_code_map` enumerates CMap lookup ranges and writes entries in blocks of up to 100, selecting `begincidchar`, `begincidrange`, `beginbfchar`, `beginbfrange`, or notdef equivalents based on key/range and value type.

The public entry point is `psf_write_cmap`. It validates `CMapType`, writes the resource header unless the CMap is a ToUnicode map, writes fixed CMap dictionary fields, emits code-space ranges, emits notdef and normal mappings, then closes the CMap resource.

Important behavior:
- Multi-font CMaps emit `usefont` when the lookup font index changes.
- `font_index_only` can restrict output to one descendant font's mappings and CIDSystemInfo.
- Glyph value mappings call the CMap's `glyph_name` callback and then emit names through the caller-supplied `put_name_chars` function.
- Code-space ranges are buffered in groups of 100 before emission.

This is a serialization utility only. Its main dependencies are Ghostscript CMap enumeration APIs in `gxfcmap.h` and stream/PS string helpers.
