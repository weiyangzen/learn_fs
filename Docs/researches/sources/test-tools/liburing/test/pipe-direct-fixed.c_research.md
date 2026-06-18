# sources/test-tools/liburing/test/pipe-direct-fixed.c

Purpose: validates `io_uring_prep_pipe_direct()` when creating pipes in explicit fixed-file slots, including the historic bug where non-auto slot installs reported or cleaned up slot 0.

Important APIs/types/functions: `io_uring_register_files_sparse`, `io_uring_register_files_update`, `io_uring_prep_pipe_direct`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_FIXED_FILE`, and fixed slot indexes.

Control flow: `test_specific_slots()` creates a fixed pipe at requested slot and slot+1, verifies returned indexes, then writes/reads through fixed slots. It runs for slot 5 and slot 0. `test_no_clobber_slot0()` installs a sentinel pipe read-end at slot 0, creates another fixed pipe at slots 5/6, and verifies slot 0 still reads sentinel data.

State and persistence behavior: fixed-file table entries and pipe fds are transient. No files.

Dependencies and integration points: requires sparse fixed-file support and pipe-direct opcode support; `-EINVAL` marks no-pipe skip.

Risks and test signals: failures are wrong returned slot indexes, broken fixed pipe communication, or clobbering slot 0 during nonzero slot installation/cleanup.
