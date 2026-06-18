# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.c

## Role

`gschar.c` implements Ghostscript library “character writing” wrappers around the lower-level text enumeration API.

This is text rendering/control flow infrastructure, not filesystem code.

## Main Public Functions

Initialization wrappers:

- `gs_show_n_init`
- `gs_ashow_n_init`
- `gs_widthshow_n_init`
- `gs_awidthshow_n_init`
- `gs_kshow_n_init`
- `gs_xyshow_n_init`
- `gs_glyphshow_init`
- `gs_glyphpath_init`
- `gs_glyphwidth_init`
- `gs_cshow_n_init`
- `gs_stringwidth_n_init`
- `gs_charpath_n_init`
- `gs_charboxpath_n_init`

Enumerator/control functions:

- `gs_show_enum_release`
- `gs_show_next`
- `gs_show_width_only`

Accessors:

- `gs_show_current_char`
- `gs_show_current_glyph`
- `gs_show_current_width`
- `gs_kshow_previous_char`
- `gs_kshow_next_char`
- `gs_show_width`

Cache/metrics operators:

- `gs_setcachedevice_double`
- `gs_setcachedevice_float`
- `gs_setcachedevice2_double`
- `gs_setcachedevice2_float`
- `gs_setcharwidth`

## Important Behavior

- Each initializer calls the matching `gs_*_begin` lower-level text routine, then passes the result through `show_n_begin`.
- `gs_kshow_n_init` rejects composite and CID font types with `gs_error_invalidfont`.
- `gs_setcachedevice*` and `gs_setcharwidth` reject calls when the enumerator’s graphics state does not match the supplied `gs_state`.
- Float cache-device APIs are backward-compatible wrappers that convert arrays to double and call the double implementation.
- `gs_show_next` delegates to `gs_text_process`.

## Internal `show_n_begin`

`show_n_begin` forces the result enumerator to be a `gs_show_enum`.

If the current device’s `text_begin` created a different text enumerator type, the function:

- saves the device’s current `text_begin` procedure
- releases the existing text enumerator
- temporarily resets `text_begin` to `gx_default_text_begin`
- starts text enumeration again
- restores the original device procedure
- copies the resulting `gs_show_enum` into the caller-provided storage
- frees the temporary allocated enumerator

## Dependencies

Includes Ghostscript graphics state, device, matrix, coordinate, memory device, character, and font internals.

## Notable Risks

- `show_n_begin` copies a structure by value, then frees the original allocation. This depends on the enumerator owning only relocatable/reference-managed internals that remain valid after the shallow copy.
- `gs_kshow_next_char` indexes directly into `penum->text.data.bytes[penum->index]`; correctness depends on enumeration state.
