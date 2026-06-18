# File Research: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.c

- Purpose: open-addressed pointer hash table implementation.
- Key behavior: stores metadata in common pointer bits, uses `(void *)1` as deleted marker, tracks deleted slots, and grows/rehashes when table is too full.
- APIs implemented: init, sized init, clear, copy, add, delete, iterator traversal, random pick, custom allocator, and consistency check.
- Invariants: elements must be non-NULL and not `(void *)1`; caller supplies hashes and a rehash callback.
- Debugging: `htable_check` validates that every element can find itself via its rehash.
