# sources/test-tools/strace/src/statfs.c

Purpose: decodes `statfs` path and output filesystem-stat buffer.

Important APIs/types/functions: `SYS_FUNC(statfs)`, `printpath`, and `print_struct_statfs`.

Control flow: entry prints pathname; exit prints `buf` via the common statfs printer.

State and persistence behavior: stateless; output buffer is read only on exit.

Dependencies and integration points: depends on architecture-specific statfs fetch/print support behind `print_struct_statfs`.

Risks: `statfs` layout varies by architecture; wrapper correctness depends on the common printer.

Test signals: valid statfs, invalid buffer, unknown filesystem magic, and path decode failure.
