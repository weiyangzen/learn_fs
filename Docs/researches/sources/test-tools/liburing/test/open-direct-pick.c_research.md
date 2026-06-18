# sources/test-tools/liburing/test/open-direct-pick.c

Purpose: tests auto-allocation of direct fixed-file slots via `file_index = UINT_MAX` and exhaustion behavior.

Important APIs/types/functions: `io_uring_register_files_sparse`, `io_uring_prep_openat_direct`, `io_uring_prep_close_direct`, `UINT_MAX`, `FDS=800`, and `t_create_file`.

Control flow: registers an 800-slot sparse table, opens the same file 800 times into auto-picked slots, randomly closes 100 occupied slots, opens 100 more successfully, then attempts one extra open expecting `-ENFILE`.

State and persistence behavior: creates `/tmp/.open.direct.pick` and unlinks it. Fixed-file table occupancy is the tested state.

Dependencies and integration points: depends on sparse file registration and direct slot picking support. `-EINVAL` on first auto-pick marks feature unsupported and exits successfully.

Risks and test signals: failures are bad auto-pick error handling, inability to reuse closed slots, wrong full-table error, or random close loop not finding occupied slots.
