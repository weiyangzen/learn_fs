# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.h

Generic dictionary stack API. It defines `ds_ptr` and `const_ds_ptr`, declares GC cleanup and full-stack name lookup, and provides fast macros for name lookup.

Key macros:
- `dstack_find_name_by_index_inline`: one-probe top-dictionary fast path, otherwise calls full search.
- `if_dstack_find_name_by_index_top`: checks only the top dictionary.

The comment notes the top-dictionary fast path hits over 90% of name lookups excluding operators.
