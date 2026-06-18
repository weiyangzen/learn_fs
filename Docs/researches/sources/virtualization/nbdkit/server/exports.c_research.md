# File Research: sources/virtualization/nbdkit/server/exports.c

Purpose: Implements the public `struct nbdkit_exports` list used by plugins and filters to enumerate available NBD exports.

Data model:
- Wraps a vector of `struct nbdkit_export`.
- Tracks `use_default`, a sentinel asking the server to insert the backend default export later.
- Caps the list at `MAX_EXPORTS` = 10000 to limit memory and protocol reply size.

Public API:
- `nbdkit_exports_new` allocates an empty export list.
- `nbdkit_exports_free` frees each export name/description and the vector.
- `nbdkit_exports_count` returns vector length.
- `nbdkit_get_export` returns an export by index, with an assert on bounds.
- `nbdkit_add_export` duplicates the name and optional description after enforcing `NBD_MAX_STRING` limits.
- `nbdkit_use_default_export` sets the sentinel.

Server integration:
- `exports_resolve_default(exps, b, readonly)` resolves `use_default` through `backend_default_export`, clears the sentinel, and appends the resulting export.

Error behavior:
- Allocation and length failures call `nbdkit_error` and set useful `errno` values.
