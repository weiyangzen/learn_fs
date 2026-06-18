# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstypes.h

Purpose: Defines common Ghostscript library scalar and geometry types used broadly by graphics, font, image, and memory code.

Key definitions:
- `gs_id` and `gs_no_id` for Ghostscript-generated unique IDs.
- `gs_string`, `gs_const_string`, and `gs_param_string` for sized byte strings.
- `gs_bytestring` and `gs_const_bytestring` for strings that may point inside a GC-visible byte object.
- `gs_point`, `gs_int_point`, `gs_log2_scale_point`, `gs_rect`, `gs_int_rect`, and `gs_range_t`.

Behavior:
- String types explicitly store `data` plus `size`, avoiding reliance on NUL termination.
- Bytestring variants preserve the owning byte allocation pointer for garbage collection.
- Rectangle comments define integer/real rectangle interval conventions: rectangles are half-open, ranges are closed.

Dependencies:
- Assumes basic Ghostscript primitive types such as `byte`, `uint`, `ulong`, and `bool` are already defined.

Notable risks:
- Many downstream structures rely on `data,size` being first for GC scanning consistency.
