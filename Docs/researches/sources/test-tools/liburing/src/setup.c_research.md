<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/setup.c -->
## sources/test-tools/liburing/src/setup.c

Purpose: implements ring setup, mmap/no-mmap memory layout, teardown, probe allocation, memory-size helpers, memlock-size helpers, and provided-buffer-ring allocation/free helpers.

Important APIs/types/functions: setup internals include `get_sq_cq_entries`, `io_uring_mmap`, `io_uring_alloc_huge`, `__io_uring_queue_init_params`, and `io_uring_queue_init_try_nosqarr`. Public APIs include `io_uring_queue_mmap`, `io_uring_ring_dontfork`, `io_uring_queue_init_mem`, `io_uring_queue_init_params`, `io_uring_queue_init`, `io_uring_queue_exit`, `io_uring_get_probe_ring`, `io_uring_get_probe`, `io_uring_free_probe`, `io_uring_memory_size*`, `io_uring_mlock_size*`, `io_uring_setup_buf_ring`, and `io_uring_free_buf_ring`.

Control flow: setup validates entry counts, optionally allocates user/no-mmap ring memory, calls `io_uring_setup`, maps SQ/CQ/SQE regions or uses supplied memory, initializes ring pointers and SQ array indexes, records feature/flag/fd state, and sets internal CQ-enter flags for IOPOLL. Teardown unmaps or preserves app memory, unregisters ring fd if needed, and closes the ring fd. Buffer-ring setup either maps kernel-provided rings on hppa or allocates anonymous memory and registers it on other architectures.

State and persistence behavior: initializes all `struct io_uring` fields, shared ring mappings, kernel ring fd, registered-ring internal flags, SQ/CQ masks and entries, and app-memory ownership. Probe helpers allocate temporary probe buffers and sometimes temporary rings.

Dependencies and integration points: uses syscall wrappers, `setup.h`, `int_flags.h`, `liburing.h`, `io_uring.h`, page size helpers, and register wrappers for probe and buffer rings.

Risks: ring memory calculations are ABI- and page-size-sensitive, especially with `IORING_SETUP_SQE128`, `IORING_SETUP_CQE32`, `IORING_SETUP_NO_SQARRAY`, and huge-page no-mmap mode. Error cleanup must avoid unmapping app-owned memory and must close fds after partial setup failures. Registered-fd-only requires no-mmap and updates fd ownership.

Test signals: `across-fork.c` checks fork mapping behavior; setup tests and no-mmap/init-mem tests validate memory sizing and supplied memory paths; accept SQPOLL tests exercise setup flags and feature negotiation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/setup.c -->
