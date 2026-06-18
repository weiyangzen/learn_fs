<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/sanitize.h -->
## sources/test-tools/liburing/src/include/liburing/sanitize.h

Purpose: declares sanitizer hooks used when liburing is built with address-sanitizer support. Without `CONFIG_USE_SANITIZER`, the same function names compile to no-op macros.

Important APIs/types/functions: declares `liburing_sanitize_ring`, `liburing_sanitize_address`, `liburing_sanitize_region`, and `liburing_sanitize_iovecs` when sanitizer support is enabled; otherwise each macro expands to an empty do-while block.

Control flow: `queue.c` calls `liburing_sanitize_ring` before submit, and `register.c` calls address/iovec sanitizers before kernel registrations. The implementation in `sanitize.c` checks submitted SQE addresses by opcode.

State and persistence behavior: no state is owned. Sanitizer mode may terminate the process on poisoned memory before a syscall reaches the kernel.

Dependencies and integration points: paired with `sanitize.c` and controlled by generated config defines. It keeps production builds free of ASAN runtime dependency.

Risks: the no-op path means normal builds rely on kernel/user errors rather than early ASAN diagnostics. The enabled path must stay synchronized with `IORING_OP_LAST`.

Test signals: the test Makefile adds sanitizer flags when configured; syzkaller-derived tests are compiled out or skipped under some sanitizer modes to avoid incompatibilities.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/sanitize.h -->
