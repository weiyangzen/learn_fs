# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.c

Purpose: implements Ghostscript interpreter VM save/restore/forgetsave management. It treats `save` as a transactional boundary over ref-memory chunks, change chains, local/global VM spaces, names, streams, font caches, and allocator state.

Core mechanisms:
- `alloc_save_state` creates visible save IDs, optionally saves global VM for the outermost local save, captures current allocator chunks, creates inner chunks for unallocated regions, resets free lists, and marks the interpreter as in-save.
- `alloc_save_change_in` records old slot contents in an `alloc_change_t` chain when an old ref slot is modified during a save level, preserving enough location metadata for static refs, dynamic refs, and refs embedded in structs.
- `alloc_restore_step_in` finalizes objects that will be freed, restores auxiliary resources, replays saved ref contents, frees chunks allocated after the save, restores allocator state, and resets or recomputes `l_new` markings.
- `alloc_forget_save_in` commits a save by merging current chunks/free lists/change chains into the next outer save, or clears bookkeeping when committing the outermost save.
- `alloc_restore_all` unwinds all save levels, finalizes memory spaces, releases non-memory resources through a fake save, and frees local/global/system memory.

Important details:
- `l_new` is a slot-level marker used to decide whether a slot modification needs undo logging. `save_set_new` scans change chains and newly allocated ref objects to set or clear this bit.
- To avoid repeated expensive scans at deep save levels, the code creates invisible internal saves after scanning more than `max_repeated_scan`.
- `alloc_is_since_save` and name variants detect whether a pointer/name would become dangling after restore by checking chunks allocated since the target save.
- GC support for `alloc_change_t` relocates both the saved content and the referenced slot address, including the embedded-struct offset case.

Dependencies: `gs_ref_memory_t`, chunk allocator internals, ref packing, name table restoration, stream lists, font cache restore hooks, VM-space checks, and Ghostscript GC structure descriptors.

Research notes:
- This is interpreter memory-transaction code, not filesystem logic, but it is central to safe PostScript execution in the vendored Plan 9 Ghostscript tree.
- Comments explicitly describe save as "start transaction", restore as abort, and forgetsave as commit.
