# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.h

Declares generic dictionary-stack APIs and fast lookup macros.

Key points:
- Defines dictionary stack pointer aliases `ds_ptr` and `const_ds_ptr`.
- Declares GC cleanup and full name-index lookup.
- Defines `dstack_find_name_by_index_inline`, an optimized top-dictionary single-probe lookup that falls back to full search.
- Defines `if_dstack_find_name_by_index_top`, a macro that only checks the top dictionary.
- Includes dictionary-stack data and generic stack headers.

Research notes:
- The inline lookup is tuned for common interpreter name lookup, with comments claiming over 90 percent top-dictionary single-probe hits outside operator handling.
