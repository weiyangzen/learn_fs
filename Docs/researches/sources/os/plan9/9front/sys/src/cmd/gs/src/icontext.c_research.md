# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.c

Implements interpreter context state allocation, load, store, and free operations.

Key behavior:
- Defines GC clear-mark, enumerate, and relocate procedures for `gs_context_state_t`, including embedded dual memory and stack objects.
- `context_state_alloc` allocates the context in local VM if needed, allocates interpreter stacks, initializes dictionary stack systemdict, allocates graphics state, copies memory state, initializes language/user/runtime fields, creates `userparams`, initializes bogus stdio file refs, and increments VM context counts.
- `context_state_load` switches references from systemdict to context-local objects using `userdict.localdicts`, installs saved `userparams`, calls `set_user_params`, restores save-check state, clears execution-stack cache, and refreshes dictionary-stack top cache.
- `context_state_store` cleans dictionary/exec/operand stacks and saves `systemdict.userparams` into the context.
- `context_state_free` decrements VM context counts and either reports freed VM spaces or frees graphics state and interpreter stacks.
- Graphics state freeing uses `grestoreall`, pointer patching for the final restore, and `gs_state_free`.

Research notes:
- Context switching is tightly coupled to systemdict/userdict and local/global VM semantics.
- Some cleanup paths are marked with comments for freeing whole VM spaces or userparams, suggesting implementation gaps or higher-level ownership.
