# File Research: sources/os/bsd/netbsd-src/lib/libform/form.c

## Purpose
Implements public form object management APIs: windows, options, hooks, field attachment, page/current-field state, allocation/freeing, data visibility, and cursor positioning.

## Main Components
- Defines `_formi_default_form`, the prototype for new/default forms.
- Window APIs manage form window, subwindow, and output window, rejecting changes while posted.
- `scale_form()` computes minimum rows/columns required for attached fields.
- User pointer, option, and hook APIs manage form metadata.
- `set_form_fields()` validates and attaches fields, disconnects old fields, assigns indexes/pages, computes page starts, sorts fields, and stitches navigation links.
- `form_fields()` and `field_count()` expose attached field metadata.
- `move_field()` moves disconnected fields only.
- Page/current-field APIs manage selected page and field with state checks.
- `new_form()` allocates a form from defaults, defaults screen output to `stdscr`, and optionally attaches fields.
- `free_form()` refuses posted forms and detaches fields.
- `data_ahead()` / `data_behind()` report offscreen data around the current field.
- `pos_form_cursor()` positions the curses cursor based on current field visibility and cursor offsets.

## Integration
Depends on `internals.h` helpers for page discovery, field sorting, navigation stitching, and debug output. Used by `driver.c`, `post.c`, and application-facing curses form code.

## Risks / Notes
- Form state is invalid to mutate while posted in several APIs.
- Field/page numbering is tightly coupled to `_formi_find_pages()` and driver request behavior.
- `data_ahead()` is marked with an internal `XXXX wrong` comment, indicating known uncertainty.
