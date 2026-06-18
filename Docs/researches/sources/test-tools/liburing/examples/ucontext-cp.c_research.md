# sources/test-tools/liburing/examples/ucontext-cp.c

## sources/test-tools/liburing/examples/ucontext-cp.c

Purpose: Demonstrates coroutine-style asynchronous file copying using `ucontext` plus io_uring completions.

Important APIs/types/functions: `async_context`, `arguments_bundle`; generated `await_readv`/`await_writev` macros; `await_delay`; `setup_context`; `copy_file`; `copy_file_wrapper`; `swapcontext`, `makecontext`, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_prep_timeout`.

Control flow: main initializes a ring, creates one coroutine per input/output pair, starts each until it submits its first awaited operation, then enters an event loop. Await helpers prepare an SQE tagged with the coroutine context and swap back to main. Main waits for completions, retrieves context from CQE data, and resumes the coroutine. Completed coroutines update success/failure counters and main frees their stacks.

State and persistence: output files, per-coroutine heap stack, bundle, iovec buffer, and shared success/failure counters.

Dependencies/integration: `ucontext.h` availability detected by configure, liburing, POSIX files and timer operations.

Risks: `ucontext` is obsolete/nonportable and conditionally built. `makecontext` function-pointer cast is nonportable. Short writes fail rather than retry. The code mutates `piov->iov_len` after short reads and does not restore it to `BS` for the next loop, so subsequent reads may stay short.

Test signals: printed coroutine operation trace and final success/failure counts; output comparison can validate copies.
