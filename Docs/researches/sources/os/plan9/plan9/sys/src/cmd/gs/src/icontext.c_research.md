# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.c

Implements interpreter context state lifecycle and GC support.

Main responsibilities:
- GC descriptor enumerates/relocates graphics state, stdio refs, userparams, dual memory, and dictionary/execution/operand stacks.
- `context_state_alloc` allocates stacks, initializes `system_dict`, allocates graphics state, copies dual memory, creates `userparams`, initializes scanner/security flags and invalid stdio refs, and increments VM context counts.
- `context_state_load` copies context-local dictionary entries into `systemdict`, installs saved `userparams`, resets user parameters, restores save checking, clears estack caches, and refreshes dictionary-stack top cache.
- `context_state_store` cleans ref stacks and saves `systemdict.userparams`.
- `context_state_free` decrements VM context counts, returns a freed-space mask if any VM is last-owned, otherwise tears down graphics state and stacks.

This file is important for multi-context Display PostScript support, though the broader API still limits instances.
