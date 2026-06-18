# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontext.c

Implements Display PostScript context, scheduler, lock, condition, monitor, fork/join, yield, and context-aware `usertime` operators.

Key behavior:
- Defines `gs_context_t`, `gs_scheduler_t`, locks, conditions, context lists, and GC descriptors.
- Initialization hooks interpreter reschedule/time-slice callbacks, creates a scheduler in system memory, wraps VM reclaim, and creates the initial context.
- Scheduler keeps active contexts by index, supports time slicing, handles dead-context destruction, and enforces local-VM save-level restrictions so contexts sharing local VM cannot run while another has unmatched saves.
- `context_reclaim` hides contexts outside the current local VM during GC, then restores visibility after collection.
- Operators include `condition`, `currentcontext`, `detach`, `.fork`, `join`, `.localfork`, `lock`, `monitor`, `notify`, `wait`, `yield`, and replacement `usertime`.
- `.fork` creates a new context sharing local/global VM; `.localfork` creates private local VM with shared global VM and a new `userdict`.
- Fork setup copies dictionary/execution/operand stacks, stdio refs, language level, binary object format, and for shared-VM forks copies graphics-state stack.
- `fork_done` unwinds stacks/gstates, performs pending restores, handles detached contexts, wakes joiners, and reschedules.
- `monitor` acquires a lock, pushes cleanup/release continuations, and executes the protected procedure.
- `wait` releases a lock, queues the context on a condition, and reacquires the lock through `await_lock` after notify.
- `usertime` begins per-context usertime accounting lazily and returns elapsed execution time for the current context.

Dependencies and coupling:
- Deeply coupled to interpreter context state, ref stacks, VM spaces, GC roots, graphics state, files/stdin/stdout refs, and interpreter scheduling hooks.
- Uses context indices rather than cross-local-VM pointers for wait/active lists.
- Comments flag incomplete cleanup areas around freeing local VM/gstates and error handling during fork restore paths.
