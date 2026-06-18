# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isstate.h

Purpose: defines `alloc_save_t`, the saved-state object used by `isave.c`.

Fields:
- Embedded `gs_ref_memory_t state` must be first, allowing saved allocator state to be treated as a memory-state snapshot.
- `vm_spaces spaces` records the saved local/global/system memory layout.
- `restore_names` controls whether name-table entries are rolled back.
- `is_current` remembers whether this memory space was the current allocator.
- `id` stores the externally visible save ID, with zero used for invisible internal saves.
- `client_data` carries caller-owned data through save/restore.

The file also defines the private GC descriptor macro that subclasses `st_ref_memory` and adds `client_data`.
