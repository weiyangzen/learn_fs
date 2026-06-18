# File Research: sources/os/bsd/netbsd-src/lib/libform/driver.c

## Purpose
Implements `form_driver()`, the central request dispatcher for curses forms.

## Main Components
- `traverse_form_links()` moves from the current field through left/right/up/down neighbor pointers until an active visible field is found.
- `form_driver()` validates form state, posted state, and attached fields before processing input.
- Printable and blank characters are inserted into the current field through `_formi_add_char()`, respecting `O_EDIT` and `O_AUTOSKIP`.
- Page and field navigation requests validate current field data, call termination hooks, move page/field state, and call init hooks.
- Field motion, scrolling, insertion, deletion, clearing, overlay/insert mode, and validation requests are delegated to `_formi_manipulate_field()`, `_formi_validate_field()`, and `_formi_field_choice()`.
- Overloaded backspace/newline behavior maps to previous/next field when `O_BS_OVERLOAD` or `O_NL_OVERLOAD` applies.
- After successful updates, it redraws changed fields/pages, positions the cursor, and refreshes the form window.

## Integration
Uses public request constants from `form.h` and internal helpers from `internals.h`.

## Risks / Notes
Request ordering in `form.h` is semantically important. Recursive autoskip through `form_driver()` must detect loops when fields are full.
