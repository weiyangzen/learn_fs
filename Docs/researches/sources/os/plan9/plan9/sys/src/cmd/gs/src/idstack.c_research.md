# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.c

Implements dictionary-stack lookup and cache maintenance.

Main functions:
- `dstack_dict_is_permanent`: checks permanent stack dictionaries.
- `dstack_find_name_by_index`: searches from top dictionary down using packed/unpacked dictionary probing, then slower extension-block search if needed.
- `dstack_set_top`: refreshes fast top-dictionary lookup cache and `def_space`.
- `dstack_gc_cleanup`: after GC, scans permanent dictionaries and updates cached value pointers stored in names.

The fast inline path in `idstack.h` is supported by `top_keys/top_npairs/top_values`, and debug builds gather lookup/probe/depth statistics.
