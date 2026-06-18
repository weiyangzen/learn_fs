# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.c

Implements dictionary-stack lookup and cache maintenance.

Key behavior:
- In debug builds, gathers lookup/probe/depth statistics.
- `dstack_dict_is_permanent` checks whether a dictionary appears in the permanent bottom portion of the dictionary stack, handling single-block and extended stacks.
- `dstack_find_name_by_index` searches dictionaries from top to bottom for a name index.
- Packed dictionaries use the same packed-search macros as `idict.c`; unpacked dictionaries probe full ref keys.
- If the current stack block misses and extensions exist, slower `dict_find` searches remaining stack entries.
- `dstack_set_top` caches packed key/value pointers and pair count for readable packed top dictionaries, otherwise installs dummy packed keys; it also caches `def_space`.
- `dstack_gc_cleanup` scans permanent dictionaries after GC and relocates cached single-definition name value pointers.

Research notes:
- This file is a performance-critical companion to dictionary implementation.
- The inline fast path in the header is backed by this full-stack search.
