# sources/test-tools/liburing/test/lfs-openat.c

Purpose: tests `openat` through io_uring with `O_LARGEFILE`, including linked and drained interactions with blocked pipe reads during ring flush/exit.

Important APIs/types/functions: `open_io_uring`, `prepare_file`, `test_linked_files`, `test_drained_files`, `io_uring_prep_openat`, `io_uring_prep_readv`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `IOSQE_ASYNC`, `dup(ring.ring_fd)`, and `io_uring_queue_exit`.

Control flow: `main()` prepares a sparse `/tmp/io_uring_openat_test`, verifies a direct io_uring open, then submits linked read/open combinations and drained NOP/open combinations. The pipe read intentionally blocks, then a duped ring fd is closed to trigger kernel flush behavior before ring exit.

State and persistence behavior: creates a temporary sparse file with data past 4 GiB and removes it at exit. The tested state is in-flight request dependency state during file table and ring cleanup.

Dependencies and integration points: depends on pipe blocking semantics, `O_PATH` directory fd for `/tmp`, and kernel handling of linked/drained requests on ring teardown.

Risks and test signals: main risk is hangs during close/flush when blocked reads coexist with linked or drained openat requests. Any submit/open error, failed dup, or hang is a failure signal.
