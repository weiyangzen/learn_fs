# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/callcontext.c

This file implements libpuffs call contexts, which are stackful user-level contexts used to dispatch filesystem requests and yield back to the main loop. Each `puffs_cc` normally lives at the base of an mmap-allocated, aligned stack region with a guard page. `puffs_fakecc` disables real context switching for a volatile single-context mode.

`puffs__cc_create` either reuses a context from the per-mount magazine or allocates one with `slowccalloc`, initializes `ucontext_t` state, assigns stack bounds, and uses `makecontext` to start a supplied `puffs_ccfunc`. `puffs_cc_continue`, `puffs_cc_yield`, `puffs__cc_cont`, and `puffs__goto` coordinate `swapcontext`/`setcontext` transitions among request contexts, borrowed contexts, and the main loop. `puffs_cc_schedule` queues a context for later dispatch.

The file also stores caller pid/lid metadata, recovers the current context by masking the current stack address to the aligned stack base, saves/restores the main context, caches destroyed contexts up to `PUFFS_CCMAXSTORE`, and unmaps extras at exit.

Risks are high: stack alignment assumptions, guard-page placement, context lifetime, borrowed-context races if made multithreaded, and nonportable pointer passing through `makecontext`.
