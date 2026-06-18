# File Research: sources/os/linux/linux/fs/xfs/scrub/rcbag.h

## Role
Declares the public refcount-bag API.

## API
- Lifecycle: `rcbag_init`, `rcbag_free`.
- Mutation/query: `rcbag_add`, `rcbag_count`.
- Sweep helpers: `rcbag_next_edge`, `rcbag_remove_ending_at`.
- Diagnostics: `rcbag_dump`.

## Integration
The API is intentionally opaque: callers see `struct rcbag` but not the in-memory btree internals.
