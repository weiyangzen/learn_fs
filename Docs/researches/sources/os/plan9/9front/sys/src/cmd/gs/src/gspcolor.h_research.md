# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.h

Defines the client interface and base structures for Ghostscript Pattern colors.

Key structures:
- `gs_pattern_template_t`: common Pattern template fields, including type, PatternType, uid, and client data.
- `gs_pattern_instance_t`: reference-counted instance with type, saved graphics state, and pattern id.

Exports:
- `gs_setpattern`
- `gs_setpatternspace`
- `gs_make_pattern`
- `gs_get_pattern`
- `gs_pattern_reference`

Also defines public GC descriptors for subclassing Pattern templates and instances.
