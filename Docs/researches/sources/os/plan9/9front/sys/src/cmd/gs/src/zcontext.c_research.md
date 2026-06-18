# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontext.c

This file implements Display PostScript context operators: cooperative scheduling, fork/join, detach, locks, conditions, monitor/wait/notify, yield, and context-aware usertime.

Key behavior:
- Defines `gs_context_t`, `gs_scheduler_t`, `gs_lock_t`, and `gs_condition_t`.
- Hooks Ghostscript interpreter scheduling callbacks on initialization, creates the initial context, and installs a scheduler.
- Maintains active/dead/waiting context lists using context IDs rather than raw pointers.
- Handles time slicing through `ctx_time_slice` and explicit rescheduling through `ctx_reschedule`.
- Wraps VM reclaim/GC so contexts in other local VMs can be hidden during local collection.
- Implements:
  - `currentcontext`
  - `detach`
  - `.fork`
  - `.localfork`
  - `join`
  - `yield`
  - `condition`
  - `lock`
  - `monitor`
  - `notify`
  - `wait`
  - context-aware replacement for `usertime`
- Supports local forks with private local VM and shared global VM, including userdict replacement and stack copying.
- Supports regular forks sharing local/global VM, including gstate stack copying.
- Cleans up terminated contexts, restores stacks/gstate, processes unmatched saves, and schedules joiners.
- Implements locks and conditions with waiting lists and monitor cleanup continuations to release locks on normal completion or stack unwinding.

Important dependencies:
- Uses interpreter state storage/loading from `icontext.h`.
- Uses VM/save/GC internals from `isave.h`, `istruct.h`, and allocator APIs.
- Uses file refs for fork stdin/stdout setup through `files.h`.
- Integrates with operand, dictionary, and execution stacks through `ostack.h`, `dstack.h`, and `estack.h`.

Research notes:
- This is the most OS-like file in the group: it models lightweight interpreter contexts and synchronization primitives.
- It is explicitly cooperative, not kernel-thread based.
- The source contains several cautionary comments around local VM save levels, GC visibility, gstate copying, and incomplete/freeing cleanup paths.
