# sources/test-tools/liburing/test/vec-regbuf.c

Purpose: validates fixed registered-buffer vector operations for writev/sendmsg zero-copy and readv. It stresses registered vector boundaries, segment resizing, aligned/unaligned spans, invalid iovecs, and readback correctness.

Important APIs/types/functions: `struct buf_desc`, `struct work`, `probe_support`, `bind_ring`, `reinit_ring`, `init_buffers`, `verify_data`, `test_rw`, `test_sendzc`, `test_vec`, `test_sequence`, `test_basic`, `test_readv_fixed`, `test_readv`, `test_fail`, `io_uring_register_buffers_sparse`, `io_uring_register_buffers_update_tag`, `io_uring_prep_writev_fixed`, `io_uring_prep_sendmsg_zc_fixed`, and `io_uring_prep_readv_fixed`.

Control flow: main probes for `IORING_OP_READV_FIXED` support, allocates a guarded memory area with inaccessible guard pages, registers one buffer slot, and runs two passes: send zero-copy fixed and writev fixed. `test_basic` runs many valid iovec sequences over an IPv6 socket pair while a verifier thread reads the other side and compares bytes. `test_fail` submits zero-length and invalid/out-of-bounds iovecs and requires non-positive/error CQEs. `test_readv` creates a temp file with known data and reads it back through fixed readv for single, multi-segment, and unaligned vectors.

State/persistence behavior: uses mmaped anonymous memory for registered buffers, socket pairs for transfer, and an unlinked temporary file for readv verification. The ring is reinitialized frequently to exercise registration table update paths.

Dependencies/integration: depends on registered sparse buffer support, fixed vector op support, IPv6 socket-pair helpers, zero-copy sendmsg support, mmap guard behavior, and root or sufficient permissions for buffer registration if required.

Risks/test signals: skips if the probe lacks registered vector ops or if root-only registration blocks unprivileged runs. Failures are data mismatches, CQE byte counts not matching aggregate iovec length, invalid vectors succeeding, or registration/update errors.
