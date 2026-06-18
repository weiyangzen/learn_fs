# sources/test-tools/liburing/examples/Makefile

## sources/test-tools/liburing/examples/Makefile

Purpose: Builds liburing example programs against the in-tree static library.

Important targets/variables: `example_srcs`, `example_targets`, `helpers.o`, pattern target `%: %.c $(helpers) ../src/liburing.a`, `all`, `clean`, sanitizer/TSAN flag handling, conditional `CONFIG_HAVE_UCONTEXT`.

Control flow: include generated config unless cleaning, assemble source list, optionally add `ucontext-cp.c`, compile `helpers.o`, and link each example with `helpers.o`, `../src/liburing.a`, `-luring`, and pthread. Sanitizer options are appended when configured.

State and persistence: creates example binaries and `helpers.o`; clean removes all targets.

Dependencies/integration: depends on `config-host.mak`, `Makefile.quiet`, liburing headers from source, `../src/liburing.a`, pthread, and source files in `examples`.

Risks: `all_targets += ucontext-cp helpers.o` is outside the `CONFIG_HAVE_UCONTEXT` block, so clean may remove `ucontext-cp` even when not built. Pattern target links every C file with helpers, which is convenient but can mask unused helper coupling.

Test signals: CI `make examples` under many compilers and sanitizers.
