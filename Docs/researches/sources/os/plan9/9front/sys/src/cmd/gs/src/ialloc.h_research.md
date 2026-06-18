# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.h

Declares interpreter allocator access macros and APIs.

Key points:
- Defines current interpreter memory aliases through `i_ctx_p->memory`, including local/global/system spaces.
- Provides convenience wrappers for allocating/freeing bytes, structs, arrays, strings, and const objects through current interpreter memory.
- Declares `ialloc_init`, requested-GC reset, memory validation, VM-space accessors, and allocation-space selection.
- When refs are known, defines wrappers for ref-array allocation/resizing/freeing and string-ref allocation.
- Defines `make_istruct*` and `make_iastruct*` helpers that tag structures with the current VM space.

Research notes:
- This header is the main shorthand layer used by interpreter code.
- It hides the dual-memory structure but keeps VM-space semantics visible through attributes.
