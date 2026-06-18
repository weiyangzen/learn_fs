# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.c

Implements the Ghostscript interpreter save/restore manager. It treats `save` as a transaction boundary over the interpreter VM allocator: saving closes current chunks, creates inner chunks over unallocated regions, records free-list and allocator state, and assigns externally visible save IDs. Restoring unwinds changed ref slots, finalizes and frees newer allocations, restores allocator state, font/name resources, and can also restore global VM for the outermost local save.

The core change log is `alloc_change_t`, recording a slot address, old contents, and whether the slot lives in a static object, a ref object, or inside a struct. The file uses the `l_new` bit as a per-slot write-barrier marker, with `save_set_new` scanning changed slots and newly allocated ref blocks. It also supports invisible inner saves to reduce repeated scan costs after large allocations.

Major APIs include `alloc_save_state`, `alloc_save_change_in`, `alloc_find_save`, `alloc_is_since_save`, `alloc_restore_step_in`, `alloc_forget_save_in`, and `alloc_restore_all`. The logic is tightly coupled to GC relocation, local/global VM spaces, streams, names, and font cache restoration.
