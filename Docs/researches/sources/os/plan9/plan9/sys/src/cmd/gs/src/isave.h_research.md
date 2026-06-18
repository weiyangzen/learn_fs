# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.h

Purpose: declares the interpreter save/restore API used by PostScript VM operators and memory-management code.

Key contract:
- Save objects are represented externally by numeric save IDs rather than direct `alloc_save_t` refs, because PostScript save objects are simple objects and because direct composite save references would complicate invalidation after restore.
- `alloc_save_state` returns a nonzero save ID and stores caller client data.
- `alloc_find_save`, `alloc_save_current_id`, and `alloc_save_current` map IDs back to active save records.
- `alloc_restore_step_in` restores one externally visible save step, while `alloc_forget_save_in` commits a save without pointer recency checks.
- `alloc_is_since_save` and name helpers support restore safety checks.

The internal section documents the `new_mask`/`test_mask` optimization: while in a save, new allocations get `l_new`, and old-slot stores are undo-logged only when `l_new` is absent.

Dependencies: requires interpreter memory definitions and `idosave.h`; exposes `font_restore` as the cache cleanup hook used by `isave.c`.
