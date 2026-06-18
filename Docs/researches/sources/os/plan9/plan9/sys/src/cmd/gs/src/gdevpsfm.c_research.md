# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfm.c

This file writes Ghostscript CMap objects in standard PostScript resource syntax. It serializes CMap headers, code space ranges, notdef mappings, CID mappings, bfchar/bfrange mappings, font-index switches, and CIDSystemInfo dictionaries.

Key helpers:
- `pput_string_entry` writes a `gs_const_string` after a literal prefix.
- `pput_hex` emits bytes as lowercase hexadecimal strings.
- `cmap_put_ranges` writes `begincodespacerange` blocks, with callers batching up to 100 ranges.
- `cmap_put_system_info` writes either `null` or a `Registry`/`Ordering`/`Supplement` dictionary.
- `cmap_put_code_map` enumerates CMap lookup ranges and emits mappings in blocks of at most 100 entries.

`psf_write_cmap` is the public entry point. It validates that `CMapType` is 0, 1, or 2; emits a Resource-CMap DSC header unless writing a ToUnicode CMap; writes fixed CMap dictionary fields; emits code-space ranges; emits notdef then normal mappings; and closes the CMap resource.

Important behavior:
- Multi-font CMaps emit `usefont` whenever the lookup font index changes.
- `font_index_only` restricts output to one descendant font and selects the corresponding CIDSystemInfo.
- `CODE_VALUE_GLYPH` values are converted to glyph names through the CMap callback and emitted through the caller-provided `put_name_chars` function.
- Range/char operators are selected from CID, notdef, bfchar, and bfrange variants based on lookup key shape and value type.

This is a serialization utility only. Its main dependencies are Ghostscript CMap enumeration APIs in `gxfcmap.h`, stream formatting helpers, and PostScript string/name writers.
