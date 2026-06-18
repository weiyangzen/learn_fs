# File Research: sources/os/bsd/netbsd-src/lib/libform/field.c

## Purpose
Implements public field management APIs for curses forms: options, buffers, attributes, hooks, page flags, allocation, duplication, linking, and freeing.

## Main Components
- Defines `_formi_default_field`, the prototype used when callers pass `NULL` or allocate new fields.
- User pointer and option APIs manage field metadata and trigger redraws for posted fields.
- Justification APIs enforce valid styles and restrict justification to static single-row fields.
- `field_info()` and `dynamic_field_info()` report geometry and dynamic sizing.
- `field_buffer_init()` syncs buffer 0 into internal line structures, recalculates tab expansion, wraps fields, and redraws attached posted fields.
- `set_field_printf()` and `set_field_buffer()` populate field buffers and initialize derived line state.
- `field_buffer()` syncs internal lines back to buffers and optionally reformats multi-line fields with newline separators.
- Attribute/pad APIs manage foreground, background, and padding character.
- Field/form hook APIs set and retrieve field init/term hooks stored on `FORM`.
- Page/index APIs manage page-break flags and field index lookup.
- `_formi_create_field()` allocates and initializes field structs from a prototype.
- `new_field()` allocates buffers and initial line storage.
- `dup_field()` duplicates a field from an existing one.
- `link_field()` creates a field sharing buffer storage through the link chain.
- `free_field()` refuses connected fields and releases or unlinks field storage.

## Integration
Depends heavily on `internals.c` helpers for wrapping, tab calculation, redraw, cursor positioning, and buffer synchronization.

## Risks / Notes
- Field storage ownership is manual and subtle, especially for linked and duplicated fields.
- The source itself contains comments questioning buffer duplication behavior.
- `field_buffer()` may return either internal storage or a newly allocated reformatted copy depending on options.
