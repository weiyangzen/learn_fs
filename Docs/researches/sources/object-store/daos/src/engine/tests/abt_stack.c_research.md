# sources/object-store/daos/src/engine/tests/abt_stack.c

Purpose: standalone Argobots stack stress test. It creates one ULT with optional stack size and repeatedly allocates on that ULT stack until SIGSEGV, then reports apparent stack consumption.

Important APIs and functions: `main()` parses `--on-pool`, `--unnamed-thread`, `--check-overflow`, `--stack-size`, and `--var-size`, initializes DAOS logging and ABT, registers an alternate signal stack, and creates the test ULT either on the last pool or current xstream. `stack_fill()` records ABT-reported stack size and repeatedly calls `alloca(var_size)`. `handler_segv()` prints SIGSEGV details and exits success or failure depending on `g_check_overflow`. `signal_register()` configures `sigaltstack()` and `sigaction()`.

Control flow: after creating the ULT, `main()` yields once and expects `stack_fill()` to run until a signal terminates the process. The final `D_ASSERT(false)` should be unreachable. The signal path intentionally handles stack overflow on an alternate signal stack.

State and persistence: process-local globals record stack size, accumulated allocation, stack start/end addresses, and overflow-check mode. No persistent storage is used.

Dependencies and integration: depends on Argobots stack-introspection APIs, POSIX signals, `alloca`, and DAOS/GURT assertion/logging helpers. It is a destructive/manual test process intended to crash into the SIGSEGV handler.

Risks: `create_on_pool` is not initialized before option parsing, so omitting `-p` can leave undefined branch selection. Pointer subtraction uses `void *` arithmetic as a compiler extension. The test intentionally overflows stack and should not be run as part of generic unit tests without isolation.

Test signals: success is the handler printing stack allocation details and exiting. With `--check-overflow`, exceeding the ABT-reported stack size exits failure, allowing scripts to detect guard behavior.
