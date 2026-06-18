# sources/test-tools/liburing/test/read-write.c

Purpose: broad basic I/O regression test for io_uring reads and writes. It covers buffered and `O_DIRECT` file I/O, SQPOLL with registered files, fixed and cloned buffers, vectored and non-vectored operations, selected buffers, async worker offload, linked I/O, eventfd reads, resource-limit `-EFBIG`, and buffer removal.

Important APIs and types: `io_uring_prep_read`, `readv`, `read_fixed`, `write`, `writev`, `write_fixed`, `io_uring_register_files`, `t_register_buffers`, `io_uring_clone_buffers`, `io_uring_prep_provide_buffers`, `io_uring_prep_remove_buffers`, `io_uring_prep_poll_add`, `io_uring_prep_link_timeout`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, `IOSQE_IO_LINK`, `IOSQE_BUFFER_SELECT`, `eventfd`, `setrlimit`, and probe APIs for non-vectored read support.

Control flow: `_test_io()` opens the file in read or write mode, optionally registers buffers and files, submits `BUFFERS` I/O SQEs with sequential or random offsets, then verifies each completion length and optionally buffer-selected data contents. `__test_io()` repeats fixed-buffer cases using `io_uring_clone_buffers()` into a second ring. `main()` creates a temporary 256 KiB file, runs a matrix over write/read, buffered/direct, SQPOLL, fixed buffers, async offload, and non-vectored operations, then runs buffer-selection, pipe selected-buffer, eventfd, linked write-poll-timeout, large linked async write chains, `RLIMIT_FSIZE` `-EFBIG`, buffer removal batch/single, and nonaligned fixed-buffer cases.

State and persistence: global `vecs` hold test buffers; global flags suppress unsupported nonvec, buffer-select, or buffer-clone paths after detection. Registered files and buffers persist per ring until explicitly unregistered. Temporary test file persists across the matrix and is unlinked at the end when internally created.

Dependencies and integration: uses helper buffer/file creation and liburing probe helpers. Some subcases skip on permissions, unsupported operations, missing huge functionality, or non-root for the `EFBIG` test.

Risks and test signals: this file has high blast radius. Failures point to core read/write completion sizing, fixed-file indexing, fixed-buffer registration/clone, selected-buffer data placement, linked operation progress, resource-limit propagation, or buffer removal semantics. Passing means a large cross-product of basic I/O modes agrees with expected lengths and data.
