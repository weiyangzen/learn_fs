# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxobj.h

Ghostscript memory manager object header definitions.

Key contents:
- Defines object mark/back field bit layout and distinguished GC values for unmarked local objects and untraced global objects.
- Defines macros for setting/testing unmarked, untraced, and marked object states.
- Defines `obj_header_data_t`, including alone flag, mark/back union, object size, and type/relocation union.
- Computes object alignment modulus from memory, bitmap, and back-pointer alignment constraints.
- Defines alignment/rounding macros and the padded real `obj_header_t`.
- Defines field abbreviations for object header access.
- Defines macros to compute object content size, rounded object size, and next object when scanning storage linearly.
- Defines `chunk_head_t`, containing the relocation destination and a free object header.

Notable dependencies:
- Bitmap alignment definitions from `gxbitmap.h`.

Research notes:
- This is low-level allocator/GC metadata, not image rendering logic.
- Comments explain the dual use of mark/back during mark and compaction phases; interpreting object headers requires chunk context.
