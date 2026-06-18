<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/setup.h -->
## sources/test-tools/liburing/src/setup.h

Purpose: declares internal setup helpers shared between setup and registration code.

Important APIs/types/functions: declares `__io_uring_queue_init_params`, `io_uring_unmap_rings`, `io_uring_mmap`, and `io_uring_setup_ring_pointers`.

Control flow: no implementation here. `register.c` uses `io_uring_mmap` and `io_uring_unmap_rings` during resize, while `setup.c` implements all declarations.

State and persistence behavior: declarations cover functions that initialize or replace ring mappings and ring pointer fields.

Dependencies and integration points: included by `setup.c` and `register.c`; depends on `struct io_uring`, SQ/CQ structs, and `io_uring_params` being visible through included headers.

Risks: declarations must stay synchronized with `setup.c`; mismatches would break builds or resize/setup linkage.

Test signals: ring setup and resize tests indirectly verify these internal interfaces.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/setup.h -->
