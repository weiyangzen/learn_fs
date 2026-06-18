# File Research: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.c

This file parses and applies chmod-style mode specifications used by mksquashfs/tar processing options. It supports both octal modes and symbolic mode clauses.

Key functions:
- `parse_octal_mode_args`: accepts a single octal argument in range `0000..07777`.
- `parse_sym_mode_arg`: parses `[ugoa]*[[+-=]PERMS]+`, where `PERMS` is `[rwxXst]+` or one of `u/g/o`.
- `parse_mode_args`: dispatches octal parsing first, then symbolic parsing.
- `parse_mode`: splits a comma-separated mode string into arguments.
- `mode_execute`: applies the linked list of parsed `mode_data` operations to a `st_mode`.

Important behavior:
- Missing ownership specifier defaults to `a` with mask `0777`.
- `X` adds execute bits only for directories or files that already have at least one execute bit.
- Copy permissions such as `g=u` are encoded as negative `mode` values and expanded during execution.
- Octal mode preserves file type bits by applying `(st_mode & S_IFMT) | mode`.

Corruption/edge details:
- Syntax errors are reported through the `SYNTAX_ERR` macro with positional context when a source action string is supplied.
- `parse_mode` allocates duplicated argument strings but only frees the argv vector, not each duplicated string in this file.
