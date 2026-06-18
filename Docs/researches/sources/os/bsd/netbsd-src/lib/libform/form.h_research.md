# File Research: sources/os/bsd/netbsd-src/lib/libform/form.h

## Purpose
Public NetBSD curses form header. Defines form/field types, option flags, driver request constants, internal struct layouts, built-in field type globals, and public API prototypes.

## Main Content
- Includes curses and ETI interfaces.
- Defines field justification constants and valid range.
- Defines form options `O_BS_OVERLOAD` and `O_NL_OVERLOAD`.
- Defines field options such as visible, active, public, editable, wrap, blank, autoskip, null-ok, static, pass-ok, and reformat.
- Defines the complete ordered `REQ_*` form-driver command range from page navigation through validation and choices.
- Defines `FORM_STR`, opaque public typedefs, and internal structs for `FIELD`, `FIELDTYPE`, and `FORM`.
- Declares built-in field types: alnum, alpha, enum, integer, numeric, regexp, IPv4, IPv6, and user.
- Declares public APIs for field lifecycle, field buffers, options, attributes, hooks, validation types, form lifecycle, posting, page/current field management, windows, cursor positioning, and driver input.

## Integration
Installed as `/usr/include/form.h` and used by applications and all `libform` implementation files.

## Risks / Notes
Although public typedefs suggest abstraction, the full struct layouts are exposed in this header. The driver command ordering is explicitly called out as fragile and must remain synchronized with `driver.c`.
