# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.h

Purpose: Declares utility APIs implemented mainly by `gsutil.c` and defines object-tagging enums.

Key declarations:
- ID generation: `gs_next_ids()`.
- Memory/bitmap helper: `memflip8x8()`.
- Endian helper: `get_u32_msb()`.
- String helpers: `bytes_compare()`, `string_match()`, and `string_match_params`.
- Object tagging: `gs_object_tag_type_t`, `gs_current_object_tag()`, `gs_set_object_tag()`, `gs_enable_object_tagging()`.

Behavior:
- `string_match_params_default` is declared externally.
- Object tags include unknown, text, image, path, untouched, and a device-does-not-support value.

Dependencies:
- Includes `gxstate.h` after defining tag types because setter APIs take `gs_state *`.

Notable risks:
- Header declares object-tag functions not implemented in `gsutil.c`; they are provided elsewhere in Ghostscript.
