# sources/test-tools/strace/src/statfs64.c

Purpose: decodes `statfs64`, including the user-provided structure size parameter.

Important APIs/types/functions: `SYS_FUNC(statfs64)`, `printpath`, `PRINT_VAL_U`, and `print_struct_statfs64`.

Control flow: entry prints pathname and size. Exit prints the output buffer by passing both buffer address and user size to the statfs64 printer.

State and persistence behavior: stateless.

Dependencies and integration points: used by architectures exposing `statfs64`; depends on common statfs64 printer and path decoding.

Risks: size argument controls how much the kernel wrote and what the printer may read; wrong size handling can misdecode compat ABIs.

Test signals: expected size, short/zero/oversized size, invalid buffer, and large statfs64 values.
