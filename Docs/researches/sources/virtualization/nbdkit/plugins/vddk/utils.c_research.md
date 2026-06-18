# File Research: sources/virtualization/nbdkit/plugins/vddk/utils.c

Small utility file for the VDDK plugin.

Key behavior:
- Defines `trim(char *str)`, which removes one trailing newline if present.
- Used by VDDK log/error callback formatting to clean messages before passing them to nbdkit logging.

Dependencies:
- `vddk.h` declaration.
- Standard C string handling.
