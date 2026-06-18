# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.h

## Role

`gschar.h` declares the Ghostscript client interface for character operations and text enumeration.

This is text rendering API surface, not filesystem code.

## Main Types

- Opaque `gs_show_enum`
- Opaque `gs_font`

## Allocation And Lifetime

- `gs_show_enum_alloc(gs_memory_t *, gs_state *, client_name_t)`
- `gs_show_enum_release(gs_show_enum *, gs_memory_t *)`

The release function can optionally free the enumerator when the memory argument is non-null.

## Initialization APIs

Declares wrappers for PostScript-like text operations:

- `show`
- `ashow`
- `widthshow`
- `awidthshow`
- `kshow`
- `xyshow`
- `glyphshow`
- `cshow`
- `stringwidth`
- `charpath`
- `charboxpath`

Also declares extensions:

- `gs_glyphpath_init`
- `gs_glyphwidth_init`
- `gs_show_use_glyph`

## Enumerator Return Codes

Aliases text-processing statuses:

- `gs_show_render` = `TEXT_PROCESS_RENDER`
- `gs_show_kern` = `TEXT_PROCESS_INTERVENE`
- `gs_show_move` = `TEXT_PROCESS_INTERVENE`

Clients call `gs_show_next` until completion, error, or an intervention/rendering status.

## Accessors

- `gs_show_current_char`
- `gs_kshow_previous_char`
- `gs_kshow_next_char`
- `gs_show_current_font`
- `gs_show_current_glyph`
- `gs_show_current_width`
- `gs_show_width`
- `gs_show_in_charpath`
- `gs_show_width_only`

## Cache And Metrics APIs

- `gs_setcachedevice_float`
- `gs_setcachedevice_double`
- `gs_setcachedevice2_float`
- `gs_setcachedevice2_double`
- `gs_setcharwidth`

Macros map `gs_setcachedevice` and `gs_setcachedevice2` to the float variants for compatibility.

## Dependencies

- Includes `gsccode.h` and `gscpm.h`.
- Uses Ghostscript types such as `gs_state`, `gs_memory_t`, `gs_point`, `gs_char_path_mode`, `floatp`, `bool`, and `client_name_t`.

## Notable Risks

- API is state-machine based; clients must respond correctly to nonzero `gs_show_next` statuses.
- Some declared functions are implemented in other Ghostscript translation units, not in `gschar.c`.
