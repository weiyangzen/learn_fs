<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/sanitize.c -->
## sources/test-tools/liburing/src/sanitize.c

Purpose: provides AddressSanitizer-aware validation for SQEs and registration inputs before liburing hands pointers to the kernel.

Important APIs/types/functions: small handlers validate `sqe->addr`, `addr2`, `addr3`, `optval` regions, combinations of those fields, or no pointer. `sanitize_handlers[IORING_OP_LAST]` maps every opcode to the relevant handler and is guarded by `_Static_assert`. Public functions are `liburing_sanitize_ring`, `liburing_sanitize_address`, `liburing_sanitize_region`, and `liburing_sanitize_iovecs`.

Control flow: `liburing_sanitize_ring` walks from kernel SQ head to local SQE tail, looks up each opcode handler, and validates relevant pointer fields. On poisoned addresses or regions, ASAN describes the address and the process exits with status 1.

State and persistence behavior: no state is changed except process termination on failure. The scan reads ring SQ state and SQE contents.

Dependencies and integration points: compiled only for sanitizer-enabled builds through `sanitize.h`; depends on `<sanitizer/asan_interface.h>` and public opcode definitions. `queue.c` and `register.c` are direct callers.

Risks: handler mappings must stay in sync with `IORING_OP_LAST` and each opcode's pointer semantics. Some opcodes use fields that can be validly null or ignored by flags; overly strict checks can produce sanitizer-only false positives, while missing handlers can let bad pointers reach the kernel in tests.

Test signals: sanitizer builds and syzkaller regression tests are the primary signal. Build failure on `_Static_assert` catches new opcodes missing sanitizer coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/sanitize.c -->
