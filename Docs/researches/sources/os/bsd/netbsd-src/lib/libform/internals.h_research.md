# File Research: sources/os/bsd/netbsd-src/lib/libform/internals.h

Internal header for NetBSD `libform`. It defines shared constants, internal data structures, and prototypes used across the library’s form editor and type implementations.

Key contents:
- Direction constants `_FORMI_BACKWARD` and `_FORMI_FORWARD`.
- `DEFAULT_FORM_OPTS`, combining visible/active/public/edit/wrap/blank/autoskip/nullok/passok/static defaults.
- `FIELDTYPE` internal flag bits: `_TYPE_HAS_ARGS`, `_TYPE_IS_LINKED`, `_TYPE_IS_BUILTIN`, and `_TYPE_HAS_CHOICE`.
- Internal page descriptor, tab-stop descriptor, and field-line structures.
- Prototypes for field editing, drawing, wrapping, tab calculation, field traversal, validation, and buffer sync helpers.

This file is the private contract between `internals.c`, posting logic, and builtin field type validators.
