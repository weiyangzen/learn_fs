# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.c

Implements the generic text-processing interface between graphics state, devices, fonts, and clients.

Key behavior:
- Defines GC descriptors for `gs_text_params_t` and `gs_text_enum_t`, including string/array inputs, replacement-width arrays, devices, paths, colors, clip paths, fonts, font stacks, and cached font-matrix pairs.
- `gx_device_text_begin` validates text params, selects path/clip arguments based on operation flags, and dispatches to the device `text_begin` proc.
- `gs_text_enum_init` initializes common enumerator fields, dynamic font-stack state, current font, indexes, scale, and device refcount.
- `gs_text_enum_copy_dynamic` copies mutable enumeration state for delegated/subsidiary text processing.
- `gs_text_begin` derives the effective clip path when drawing, loads the current device color even for width-only operations, and calls the device text entry point.
- Provides begin helpers for PostScript-style operators: `show`, `ashow`, `widthshow`, `awidthshow`, `kshow`, `xyshow`, `glyphshow`, `cshow`, `stringwidth`, `charpath`, `charboxpath`, `glyphpath`, and `glyphwidth`.
- `gs_text_restart`, `gs_text_resync`, and `gs_text_process` delegate to enumerator procs.
- Accessors expose current font, current/next char, current glyph, total width, replaced widths, current width, width-only status, and cache-device setup.
- Release functions decrement device/enumerator references and call implementation-specific release hooks.
- Default font routines initialize an empty font stack, map the next input item to a char/glyph, and provide a failing `gs_no_build_char`.

Dependencies:
- Uses device text procs, font/cache structures, paths, clip paths, device colors, graphics state, and Ghostscript GC/refcount machinery.

Research notes:
- Color is loaded unconditionally because high-level devices may accumulate Type 3 charstrings even for `stringwidth`.
- `setup_FontBBox_as_Metrics2` handles CID glyph-direct cases where normal char-to-glyph setup is bypassed.
