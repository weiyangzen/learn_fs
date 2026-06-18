# File Research: sources/virtualization/guestfs-tools/gnulib/lib/hash.h

Public API for the generic hash table.

Defines:
- `Hash_tuning`
- Opaque `Hash_table`
- Callback types:
  - `Hash_hasher`
  - `Hash_comparator`
  - `Hash_data_freer`
  - `Hash_processor`

Documents:
- Table statistics and lookup APIs.
- Traversal constraints: do not resize or generally modify during traversal.
- Initialization behavior and tuning semantics.
- Ownership behavior for `data_freer`.
- Insert/remove semantics, including no duplicate and no `NULL` entry support.

Research relevance: contract for the hash table implementation.
