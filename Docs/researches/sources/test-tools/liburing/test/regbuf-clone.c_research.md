# sources/test-tools/liburing/test/regbuf-clone.c

Purpose: tests fixed-buffer cloning between rings, including registered-ring variants, unregister behavior, dummy buffers, huge-page merge behavior, offset cloning, sparse destination tables, replacement semantics, and cloning within the same ring.

Important APIs and types: `io_uring_register_buffers`, `io_uring_register_buffers_sparse`, `io_uring_clone_buffers`, `io_uring_clone_buffers_offset`, `io_uring_unregister_buffers`, `io_uring_register_buffers_update_tag`, `IORING_REGISTER_DST_REPLACE`, `io_uring_register_ring_fd`, fixed reads via `io_uring_prep_read_fixed`, and huge-page mmap flags.

Control flow: `use_buf()` performs a fixed read from a pipe into a registered buffer index and returns the CQE result, serving as a behavioral probe for whether a buffer table entry is usable. `test()` runs source/destination rings with optional registered ring fds, verifies cloning from an empty source returns `-ENXIO`, registers 64 buffers in the source, verifies destination has no buffers, clones all buffers, checks `-EBUSY` on duplicate clone, unregisters and verifies `-EFAULT`, clones in reverse, and checks double-unregister errors. `test_offsets()` checks offset overflow, too many buffers, partial clone, replacement, sparse table replacement/expansion, and usability at expected indices. `test_dummy()` clones a zero-length dummy buffer. `test_merge()` tries updating sparse entries with adjacent huge-page slices. `test_same()` clones/replaces buffers within the same ring.

State and persistence: registered buffer tables persist in each ring and are repeatedly cloned, replaced, expanded, and unregistered. Global flags record unsupported clone and offset-clone support.

Dependencies and integration: requires fixed buffers, clone APIs, and optionally huge pages. `-EINVAL` and `-ENOMEM` are feature/resource skip paths in selected cases.

Risks and test signals: incorrect error codes (`-ENXIO`, `-EBUSY`, `-EOVERFLOW`, `-EFAULT`), unusable cloned buffers, stale buffers after unregister, or wrong replacement behavior fail. Passing provides strong coverage of buffer table ownership and clone lifecycle rules.
