# sources/test-tools/stress-ng/stress-stack.c

## Purpose

`stress-stack.c` implements `stack`, a VM/memory stressor that recursively consumes stack until a fault occurs, catches the fault on an alternate signal stack, and repeats. It can fill stack pages, mlock stack regions, request pageout, or unmap stack pages to exercise stack growth, fault handling, and VM behavior.

## Important APIs, Types, and Functions

- `stress_stack_check_t` links stack frames and stores a self pointer used for stack corruption sanity checks.
- `stress_segvhandler()` handles `SIGSEGV` and `SIGBUS` by long-jumping to the recovery point.
- `stress_stack_alloc()` recursively allocates a 256 KiB local array, touches pages, optionally fills, mlocks, pageouts, or unmaps stack pages, validates recent frame links, increments bogo operations, and recurses until stop or fault.
- `stress_stack_child()` parses stack options, allocates and installs an alternate signal stack, sets parent-death alarm and OOM adjustment, installs fault handlers, wraps each recursive run in `sigsetjmp()`, and returns success/failure.
- `stress_stack()` runs the implementation under `stress_oomable_child()`.

## Control Flow

The main stressor synchronizes and then launches an oomable child. The child resolves options, defaulting aggressive mode to fill/mlock/pageout/unmap where supported, maps an alternate signal stack with `stress_mmap_populate()`, touches it with `stress_mincore_touch_pages()`, installs it via `stress_stack_sigalt()`, and marks itself OOM-killable.

The child loop installs `SIGSEGV` and `SIGBUS` handlers using the alternate stack and sets a recovery point with `sigsetjmp()`. On the initial path it calls `stress_stack_alloc()`, which creates a large stack array, touches or fills stack memory, optionally mlocks newly grown regions, optionally calls `madvise(MADV_PAGEOUT)`, optionally force-unmaps a page in the stack, validates a linked list of up to 128 previous stack frames, increments bogo, and recurses. When stack overflow or forced unmap triggers a signal, the handler long-jumps back, and the loop increments bogo again before repeating.

## State and Persistence Behavior

The stressor uses process-local signal jump state and heap/anonymous mappings for the alternate signal stack. It may mlock portions of its own stack and madvise or unmap stack pages, but all state is process-local and disappears on exit. No files are written.

## Dependencies and Integration Points

The implementation requires `siglongjmp`; otherwise it exports unimplemented. It integrates with stress-ng OOM wrappers, alternate signal stack helpers, memory-low checks, cache flush helpers, mincore helpers, forced munmap, and option parsing. It registers as `CLASS_VM | CLASS_MEMORY`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

This stressor deliberately faults and manipulates its own stack. Correct alternate signal stack setup is essential because a normal signal frame may not fit on an overflowed stack. `--stack-unmap` can create `SIGBUS`/`SIGSEGV` before natural overflow, which is expected. Mlocking stack regions can fail or create memory pressure, so the code disables mlock after failure. The recursive function passes `last_size` by value, so mlock growth tracking is local to each recursion path rather than global.

## Test Signals

Expected signals are repeated bogo increments, clean recovery from stack faults, and failure if the stack-frame self-check detects corruption. Option tests should cover `--stack-fill`, `--stack-mlock`, `--stack-pageout` on systems with and without `MADV_PAGEOUT`, and `--stack-unmap`.
