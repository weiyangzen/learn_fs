# File Research: sources/os/linux/linux-stable/fs/fs_parser.c

## Purpose
Implements the generic VFS filesystem-parameter parser used by the modern mount API. It maps textual or typed `fs_parameter` inputs to filesystem-specific option IDs and converted values.

## Key Interfaces
- `lookup_constant()` searches string-to-integer tables and is exported.
- `__fs_parse()` matches a parameter against an `fs_parameter_spec` table, handles flag negation via `no...`, warns on deprecated parameters, and dispatches type converters.
- `fs_lookup_param()` resolves string/filename parameters to `struct path`, optionally enforcing block-device input.
- Type parsers include bool, u32, s32, u64, enum, string, fd, file-or-string, uid, gid, and blockdev placeholder.
- `fs_validate_description()` optionally checks duplicate parser descriptors under `CONFIG_VALIDATE_FS_PARSER`.

## Design Notes
Flag parameters are represented by a `NULL` type callback, while value parameters call a converter function. Boolean parsing accepts `0/1`, `false/true`, and `no/yes`. UID/GID parsers convert numeric values through `current_user_ns()` and reject invalid mappings.

## Dependencies
Uses `fs_context`, `fs_parser`, VFS path lookup, current user namespace ID mapping, and per-context logging helpers from `internal.h`.

## Research Notes
The file is a central adapter between the syscall-facing mount configuration layer and filesystem-specific option tables. Error reporting is intentionally routed through mount context logging helpers so userspace can read structured diagnostics from the fscontext fd.
