# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/eqnbox.c

Concatenates two equation boxes.

Key behavior:
- Computes combined height and baseline from both operands.
- Uses class-based spacing between the right class of the left box and left class of the right box.
- Supports lineup mode by measuring and aligning to register 09.
- Appends the second box’s string to the first and frees the second register.

Filesystem relevance:
- Typesetting layout only.
