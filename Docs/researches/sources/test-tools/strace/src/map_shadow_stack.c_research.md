<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/map_shadow_stack.c -->
# sources/test-tools/strace/src/map_shadow_stack.c

Purpose: decodes `map_shadow_stack` syscall arguments.
Important APIs/types/functions: `SYS_FUNC(map_shadow_stack)`, `printaddr`, `PRINT_VAL_U`, and `shadow_stack_flags`.
Control flow: prints address, size, and symbolic flags in order and returns decoded status with hex return semantics where the common syscall layer applies it. State and persistence behavior: none.
Dependencies and integration points: memory-management syscall table entry and Linux `mman` constants. Risks: new flag constants need xlat updates. Test signals: map_shadow_stack traces with zero, known, and unknown flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/map_shadow_stack.c -->
