# sources/test-tools/stress-ng/stress-stackmmap.c

## Purpose

`stress-stackmmap.c` implements `stackmmap`, a VM/memory stressor that runs code on a file-backed mmap region used as a stack through `ucontext`/`swapcontext`. It recursively pushes data, periodically `msync()`s pages, uses guard pages, and validates stack-frame integrity until the mapped stack is exhausted.

## Important APIs, Types, and Functions

- `stress_stack_check_t` stores a previous-frame link, self pointer, and waste data for sanity checking.
- Global `ucontext_t c_main, c_test`, `stack_mmap`, `page_mask`, `page_size`, and `check_status` coordinate the alternate context and stack.
- `stress_stackmmap_push_msync()` recursively writes stack data, msyncs when crossing page boundaries, validates up to 256 linked stack frames, and recurses while the continue flag is set.
- `stress_stackmmap_push_start()` starts recursion for `makecontext()`.
- `stress_stackmmap()` creates a temporary file, maps it as the stack, maps a separate signal stack, sets guard pages with `mprotect()`, prepares the ucontext, forks children to run the mapped stack, waits for them, and cleans up.

## Control Flow

The stressor creates a temporary directory/file, opens the file with `O_SYNC`, unlinks it, truncates it to 256 KiB, maps an anonymous signal stack, and maps the file as shared writable stack memory. It applies `MADV_RANDOM`, zeroes the stack mapping, and marks the first and last pages `PROT_NONE` as guards. It initializes `c_test` with a stack region excluding guard pages and links it back to `c_main`.

After synchronization, the parent loop forks a child for each bogo iteration. The child installs a `SIGSEGV` handler on an alternate signal stack, sets OOM adjustment and parent-death alarm, initializes `check_status`, creates a context that runs `stress_stackmmap_push_start()`, and swaps from the main context to the mmap-backed stack. Recursion writes random waste values, emits addresses through stress-ng put helpers, msyncs the current page when page boundaries change, validates frame links and data complements, and keeps recursing until stop or guard-page fault. The child exits with `check_status`; the parent waits and treats nonzero child exit as failure.

## State and Persistence Behavior

The mapped stack is backed by an unlinked temporary file, so it has no lasting pathname and is removed with the temporary directory cleanup. The signal stack is anonymous. Global context and stack variables are process-local. The stressor calls `msync()` on the file-backed mapping, but the file is unlinked and removed after use.

## Dependencies and Integration Points

The file requires `ucontext.h` and `swapcontext()`; otherwise it exports unimplemented. It integrates with stress-ng temporary-file helpers, mmap helpers, signal alternate stack helpers, kill/wait helpers, OOM adjustment, scheduler settings, and continue/bogo accounting. It registers as `CLASS_VM | CLASS_MEMORY`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

`ucontext` APIs are obsolete or absent on some platforms, so the compile guard is important. Running on a deliberately small file-backed stack depends on correct guard pages and alternate signal stack setup. The static `laddr` in `stress_stackmmap_push_msync()` persists within a process and avoids repeated msyncs for the same page; each forked child starts with inherited value but only one context uses it. Temporary file creation, mmap, and mprotect failures are handled through skip/failure paths.

## Test Signals

Expected signals include successful child exits, bogo increments per child run, and no sanity mismatch logs. Filesystem tests should verify temporary directories are removed and no stack file remains. Build tests should cover absence of `swapcontext()` and runtime tests should cover `ENXIO` mmap skip paths where applicable.
