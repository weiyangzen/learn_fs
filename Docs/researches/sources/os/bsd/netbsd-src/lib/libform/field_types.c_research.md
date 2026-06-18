# File Research: sources/os/bsd/netbsd-src/lib/libform/field_types.c

## Purpose
Implements field type creation, assignment, argument handling, choices, and type linking for curses forms.

## Main Components
- `_formi_create_field_args()` processes variable arguments for field types that require arguments, including linked field types.
- `_formi_create_fieldtype()` allocates and initializes an empty `FIELDTYPE`.
- `set_field_type()` assigns a type to a field or default field and builds type-specific argument storage.
- `field_type()` and `field_arg()` retrieve type metadata from a field.
- `new_fieldtype()` creates a user field type from field and/or character validation callbacks.
- `free_fieldtype()` rejects NULL, in-use, and built-in types; linked types decrement referenced refcounts.
- `set_fieldtype_arg()` installs make/copy/free argument callbacks.
- `set_fieldtype_choice()` installs next/previous choice callbacks.
- `link_fieldtype()` creates a combined type referencing two existing types and increments their refcounts.

## Integration
Used by public form validation APIs and by built-in field type sources such as alnum, alpha, enum, integer, numeric, regex, IPv4, and IPv6.

## Risks / Notes
Linked type argument handling is complex and depends on `_TYPE_HAS_ARGS` / `_TYPE_IS_LINKED` flags from internal headers. Error handling increments an error counter rather than unwinding all partial state.
