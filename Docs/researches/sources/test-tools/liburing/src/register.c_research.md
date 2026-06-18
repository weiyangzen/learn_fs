<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/register.c -->
## sources/test-tools/liburing/src/register.c

Purpose: implements liburing's wrappers around `io_uring_register` for buffers, files, eventfds, probes, personalities, restrictions, io-wq settings, registered ring fds, provided buffer rings, synchronous cancellation, NAPI, clock selection, buffer cloning, zero-copy receive, ring resize, memory regions, iowait control, BPF filters, and query registration.

Important APIs/types/functions: `do_register` is the common path, adding `IORING_REGISTER_USE_REGISTERED_RING` when appropriate and selecting `enter_ring_fd` versus `ring_fd`. Resource APIs include `io_uring_register_buffers*`, `io_uring_register_files*`, `io_uring_register_files_update*`, `io_uring_register_files_sparse`, and unregister variants. Ring-fd APIs include `io_uring_register_ring_fd`, `io_uring_unregister_ring_fd`, and `io_uring_close_ring_fd`. Newer UAPI wrappers include `io_uring_resize_rings`, `io_uring_register_region`, `io_uring_register_bpf_filter*`, and `io_uring_register_query`.

Control flow: most wrappers validate or sanitize pointers, populate the relevant UAPI struct, and call `do_register`. File registration retries once after increasing `RLIMIT_NOFILE` on `-EMFILE`. Ring-fd registration updates `enter_ring_fd` and internal flags on success. Resize registers new sizes, mmaps a replacement ring, preserves local SQ head/tail, unmaps the old ring, and repopulates SQ array indexes.

State and persistence behavior: kernel registration state persists until unregistered or ring exit. Local `int_flags`, `ring_fd`, `enter_ring_fd`, SQ/CQ mappings, and fixed-file/buffer registration expectations change in several APIs.

Dependencies and integration points: uses `syscall.h`, `setup.h`, `int_flags.h`, sanitizer hooks, BPF/filter headers, and UAPI structs from `io_uring.h`. Accept fixed-file tests, buffer-ring tests, and ring-fd tests depend heavily on this file.

Risks: wrong `nr_args` values or struct shapes break kernel ABI calls. Registered-ring mode changes which fd is passed, so stale flags can make registrations fail or hit the wrong target. Resize must avoid leaks and preserve queue state; no-mmap rings are rejected. `io_uring_register_wait_reg` is stubbed to `-EINVAL`, which is an intentional unsupported path in this source version.

Test signals: accept fixed/direct tests, `accept-reuse.c`, buffer-ring tests, probe tests, registered-file tests, and ring resize tests cover important branches.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/register.c -->
