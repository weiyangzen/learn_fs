# sources/test-tools/liburing/test/nop-flags.c

Purpose: tests extended NOP flags that force file lookup, fixed-file lookup, registered-buffer lookup, task-work completion, injected results, and 32-byte CQE payloads.

Important APIs/types/functions: `IORING_NOP_INJECT_RESULT`, `IORING_NOP_FILE`, `IORING_NOP_FIXED_FILE`, `IORING_NOP_FIXED_BUFFER`, `IORING_NOP_TW`, `IORING_NOP_CQE32`, `IORING_SETUP_SUBMIT_ALL`, `IORING_SETUP_CQE32`, `io_uring_register_files`, `io_uring_register_buffers`, and `cqe->big_cqe`.

Control flow: first detects support by injecting result 42. It then probes bad fd behavior, validates normal and fixed file lookup, validates registered buffer lookup and bad buffer error, submits task-work NOPs, tests task-work plus injected result, checks CQE32 extra fields on a CQE32 ring, checks CQE32 rejection on a normal ring, and finally combines file/fixed-buffer/task-work flags.

State and persistence behavior: opens `/dev/null`, registers temporary file and buffer tables, and tears them down. No persistent files.

Dependencies and integration points: depends on newer kernel NOP flag support but defines missing constants locally for build compatibility. Integrates with helpers for exit statuses.

Risks and test signals: skips unsupported subfeatures. Failures include ignored lookup errors, wrong injected result, missing `big_cqe` payload, CQE32 accepted on unsupported rings, or combined flags not resolving registered resources.
