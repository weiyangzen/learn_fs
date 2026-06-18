# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.h

Declares the utility functions implemented in `gsutil.c` and defines the string-match parameter and object-tag interfaces.

Key definitions:
- ID generation API: `gs_next_ids`.
- Memory/byte helpers: `memflip8x8` and `get_u32_msb`.
- String helpers: `bytes_compare`, `string_match_params`, `string_match_params_default`, and `string_match`.
- `gs_object_tag_type_t` enum for device/object tagging values such as text, image, path, unknown, and untouched.
- Object-tag accessors: `gs_current_object_tag`, `gs_set_object_tag`, and `gs_enable_object_tagging`.

Dependencies:
- Includes `gxstate.h` for `gs_state` once object tagging APIs are declared.
