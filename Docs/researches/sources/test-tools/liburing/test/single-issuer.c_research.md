# sources/test-tools/liburing/test/single-issuer.c

Purpose: verifies ownership semantics for `IORING_SETUP_SINGLE_ISSUER` across creator, first enabler, forked children, disabled rings, SQPOLL rings, and registered-ring enter paths.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_enable_rings`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_R_DISABLED`, `IORING_SETUP_SQPOLL`, `io_uring_prep_nop`, `io_uring_submit`, fork/wait helpers, and expected `-EEXIST`.

Control flow: `try_submit()` submits and reaps a NOP. `main()` first confirms the creator can submit and a child cannot. It then tests disabled rings where a child enables first and becomes issuer, disabled rings enabled by parent rejecting child submits, SQPOLL allowing creator and child submits, and a final child rejection case after normal setup.

State/persistence behavior: state is per-ring issuer ownership and process identity across forks. No filesystem state is used.

Dependencies/integration: requires `SINGLE_ISSUER` support; `-EINVAL` skips. Uses process forking to validate cross-task behavior.

Risks/test signals: failures include allowing non-owner submit, rejecting rightful first issuer, broken SQPOLL exception behavior, or bad CQE content for allowed submits.
