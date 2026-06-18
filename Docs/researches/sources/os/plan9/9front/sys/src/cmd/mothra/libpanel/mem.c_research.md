# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/mem.c

Provides libpanel allocation helpers, default error callbacks, panel construction, and recursive free.

Key behavior:
- `pl_emalloc`/`pl_erealloc` allocate zeroed/reallocated memory or exit on failure.
- Default draw/hit/type/size/scroll callbacks abort if a panel kind has not installed behavior.
- `pl_newpanel()` initializes panel fields, appends to parent child list, assigns defaults, and allocates kind-specific data.
- `plfree()` recursively frees children, widget data, and widget-specific resources.

Important dependencies: `panel.h`, `pldefs.h`.

Notable risks:
- Creating children under panels marked `LEAF` is fatal.
- `plfree()` does not detach a freed panel from a live parent list.
