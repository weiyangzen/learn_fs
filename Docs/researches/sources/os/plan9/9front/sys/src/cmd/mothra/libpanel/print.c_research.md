# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/print.c

Debug-prints a panel tree.

Key behavior:
- Prints panel kind, pointer, rectangle, placement/fill/expand/fixed flags, padding, size, and requested size.
- Recurses through children with tab indentation.

Important dependencies: `panel.h`, flag constants.

Notable risks:
- Uses raw pointer formatting and writes directly to fd 1.
