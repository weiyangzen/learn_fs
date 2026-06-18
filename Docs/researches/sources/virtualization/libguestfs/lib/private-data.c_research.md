# File Research: sources/virtualization/libguestfs/lib/private-data.c

C API private data area attached to a `guestfs_h`.

Important behavior:
- Lazily allocates a gnulib hash table of key to opaque data pointer.
- `guestfs_set_private` replaces existing entries by key and frees only the key wrapper, not caller-owned data.
- `guestfs_get_private` returns the stored opaque pointer or NULL.
- `guestfs_first_private` and `guestfs_next_private` iterate entries, skipping entries with NULL data pointers.
- All access is protected by `g->lock`.
- Hashing uses `hash_pjw`; comparison is string equality.

Filesystem relevance:
- Lets C callers associate filesystem workflow state with a libguestfs handle without changing library internals.
