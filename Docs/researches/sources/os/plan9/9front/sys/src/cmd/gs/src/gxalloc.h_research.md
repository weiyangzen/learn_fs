# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalloc.h

Defines the internal structures, macros, and exported hooks for Ghostscript's standard reference allocator.

Key definitions:
- Documents chunk allocation layout: aligned objects and refs grow upward, strings grow downward, and string mark/relocation tables live at the top of chunks.
- Defines string mark units, relocation quanta, string-space calculations, and string free-list storage.
- Defines `chunk_t`, including object/string allocation pointers, ref object tracking, ordered chunk links, inner-chunk save/restore relationships, string free lists, and GC relocation/rescan fields.
- Provides GC structure descriptor macros for chunks and allocator state.
- Defines macros for scanning objects inside a chunk and chunks inside an allocator.
- Declares allocator chunk operations: initialize, close/open, locate, link/unlink, free, and initialize string freelists.
- Defines `gs_ref_memory_t`, a `gs_memory_t` subclass with chunk sizing, VM space, GC status, save-level state, root list, change/save lists, allocation counters, and freelists.
- Declares debug dump/find APIs under `DEBUG`.

Dependencies:
- Requires `gsmemory.h`, `gsstruct.h`, `gsalloc.h`, and `gxobj.h` definitions.
- References interpreter-level `stream` and `ref` types because allocator state tracks streams and name arrays.

Research notes:
- The comments are operationally important: inner chunks must not be freed by restore, and ref objects include dummy refs for GC relocation.
- The allocator keeps freelists last in `gs_ref_memory_t` to keep scalar offsets small.
