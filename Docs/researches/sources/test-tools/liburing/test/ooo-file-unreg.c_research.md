# sources/test-tools/liburing/test/ooo-file-unreg.c

Purpose: checks that out-of-order sparse fixed-file unregistration with an in-flight poll request does not corrupt or hang ring cleanup.

Important APIs/types/functions: `io_uring_register_files_sparse`, `io_uring_register_files_update`, `io_uring_prep_poll_add`, `IOSQE_FIXED_FILE`, UDP sockets, and `sleep`.

Control flow: registers two sparse fixed-file slots, installs two UDP sockets, submits a poll on fixed slot 0, closes the original sockets, unregisters slot 1 first and slot 0 second by updating them to `-1`, sleeps briefly, then exits the ring.

State and persistence behavior: fixed-file table state and an in-flight poll request are the tested state. No files are persisted.

Dependencies and integration points: depends on sparse fixed-file tables and socket poll behavior. `-EINVAL` for sparse registration skips.

Risks and test signals: failures are bad registration/update counts or ring exit problems after unregistering slots while fixed-file poll is pending.
