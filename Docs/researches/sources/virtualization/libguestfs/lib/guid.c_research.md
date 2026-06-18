# File Research: sources/virtualization/libguestfs/lib/guid.c

Purpose: Validates GUID string shape for internal callers.

Key behavior:
- Accepts either `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` length 36 or the same form wrapped in braces length 38.
- Requires dashes at positions 8, 13, 18, and 23.
- Requires all non-dash characters to be alphanumeric via `c_isalnum`.

Dependencies and state:
- Uses `strlen` and gnulib character classification.
- Stateless.

Risks:
- Allows any alphanumeric character, not strictly hexadecimal digits, so this validates GUID-like formatting rather than canonical GUID contents.
