# File Research: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.h

This header declares the symbolic/octal mode parser interface and the `mode_data` linked-list representation used by `symbolic_mode.c`.

Key contents:
- `SYNTAX_ERR` macro for formatted parse errors, optionally including the original action string and parse position.
- Operation constants: `SYMBOLIC_MODE_SET`, `SYMBOLIC_MODE_ADD`, `SYMBOLIC_MODE_REM`, `SYMBOLIC_MODE_OCT`.
- `struct mode_data`: linked list node with operation, mode bits, mask, and `X` flag.
- Extern declarations for parsing and execution functions.

Important behavior:
- `SYNTAX_ERR` uses allocation helpers from `alloc.h` and writes into `char **error`.
- The parser can be reused by command-line argument parsers that pass `(source, cur_ptr, args, argv, data, error)` and by direct `parse_mode`.

Dependency notes:
- Consumers must include or have available system mode bits such as `S_IFMT` where `mode_execute` is used.
- Ownership of allocated `mode_data` lists is not handled here; callers need to free when appropriate.
