# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/util.c

Shared formatting, parsing, and lookup utilities for `wsconsctl`.

Key behavior:
- Provides name tables for keyboard, mouse, display, keyboard encoding, and keyboard variants.
- `field_by_name()` resolves dotted variable names after the device prefix.
- `field_by_value()` resolves a field from its backing storage address.
- `pr_field()` prints all supported formats: integers, bools, percentages, device types, keyboard encodings, maps, calibration scale, emulations, screen types, strings, and mousecfg values.
- `rd_field()` parses input for the same formats, including merge operations, percentages with clamping, keyboard encodings/variants, keymaps through lexer/parser, calibration tuples, strings, and mousecfg values.
- `print_kmap()` serializes non-empty keymap entries.
- `print_emul()` and `print_screen()` iterate display ioctls by index.

Filesystem/OS relevance:
- Centralizes userland parsing/printing for device ioctl state.
- Keymap handling demonstrates structured parsing instead of ad hoc string mutation.
