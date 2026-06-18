# sources/test-tools/liburing/test/msg-ring.c

Purpose: broad msg-ring command suite covering self-messages, synchronous registered messages, remote-thread delivery, invalid fds, IOPOLL rings, deferred taskrun, remote submitter threads, and disabled destination rings.

Important APIs/types/functions: `io_uring_prep_msg_ring`, `io_uring_register_sync_msg`, `test_own`, `test_remote`, `test_remote_submit`, `test_invalid`, `test_disabled_ring`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_R_DISABLED`, `IOSQE_FIXED_FILE`, and pthread barriers.

Control flow: `test()` creates normal and IOPOLL rings, sends async and sync messages to self, verifies invalid regular and fixed target fds return `-EBADFD`, sends to a thread-owned ring, and under deferred-taskrun also checks remote submit and disabled-ring behavior. `main()` runs normal flags and deferred flags.

State and persistence behavior: all state is ring-to-ring CQE injection and ring fd lifetime. Fixed-file registration is temporary in invalid-fd tests.

Dependencies and integration points: depends on msg-ring opcode support, sync-msg registration support where available, IOPOLL compatibility, disabled-ring semantics, and pthread synchronization.

Risks and test signals: unsupported msg-ring or sync-msg paths are skipped. Failures include missing remote CQEs, wrong `res`/`user_data`, invalid fd not reporting `-EBADFD`, or disabled ring completion returning an unexpected code.
