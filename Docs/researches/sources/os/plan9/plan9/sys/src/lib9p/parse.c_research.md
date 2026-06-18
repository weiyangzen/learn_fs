# File Research: sources/os/plan9/plan9/sys/src/lib9p/parse.c

This file implements control-command parsing helpers for lib9p servers.

Key behavior:
- `parsecmd` copies a written command buffer, strips a trailing newline, tokenizes whitespace-separated fields, and returns a `Cmdbuf`.
- `ncmdfield` estimates the number of fields to size the `Cmdbuf` allocation.
- `respondcmderror` reconstructs a quoted command string and appends it to an error response.
- `lookupcmd` matches the first parsed field against a `Cmdtab`, supports `*` wildcard commands, and validates argument count when `narg` is nonzero.

Important dependencies:
- Uses Plan 9 `tokenize`, `quotefmtinstall`, and formatted error helpers.
- Responds through lib9p `respond`.

Notable details:
- UTF is explicitly irrelevant to field splitting; bytes are tested only against ASCII whitespace.
- `Cmdbuf`, pointer array, and copied command string are allocated as one block.
