# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht1.c

Implements `setcolorscreen`, the four-component color-screen operator. It reads four screen triples from the operand stack, one per indexed color-screen component, storing frequency, angle, and spot procedure refs.

A dummy spot function is installed before actual sampling, because real spot functions are sampled through interpreter continuations. `zsetcolorscreen` builds a `gs_halftone` with `ht_type_multiple_colorscreen`, allocates a matching `gx_device_halftone`, prepares it with `gs_sethalftone_prepare`, then schedules screen sampling for the components through `zscreen_enum_init`.

`setcolorscreen_finish` installs the prepared color halftone after all sampled screens complete. `setcolorscreen_cleanup` frees the prepared halftone/device-halftone allocations on completion or error. The implementation mirrors the single-screen flow in `zht.c` but expands it to four component dictionaries/screens.
