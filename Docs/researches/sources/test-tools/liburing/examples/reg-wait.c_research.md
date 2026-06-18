# sources/test-tools/liburing/examples/reg-wait.c

## sources/test-tools/liburing/examples/reg-wait.c

Purpose: Demonstrates registered wait arguments for `io_uring_submit_and_wait_reg`.

Important APIs/types/functions: `struct io_uring_reg_wait`, `struct io_uring_region_desc`, `struct io_uring_mem_region_reg`; `register_memory`; `io_uring_register_region`, `io_uring_enable_rings`, `io_uring_submit_and_wait_reg`.

Control flow: create pipe and ring disabled with `IORING_SETUP_R_DISABLED`, allocate page-aligned wait region, register it for wait args, enable rings, configure two wait entries. First wait expects `-ETIME` around one second with no completions. Then queue two pipe reads, satisfy one, and wait for two completions using min-wait usec; verifies submit count and approximate 10 ms wait behavior.

State and persistence: pipe fds, registered memory region, ring state. No files.

Dependencies/integration: new registered wait kernel/liburing support, page-aligned allocation helper, pipe I/O, wall-clock timing.

Risks: timing bounds are tight and may be noisy under load. Early returns leak pipe/ring/memory. Uses kernel feature detection via `-EINVAL`.

Test signals: timeout duration near expected ranges; successful registration; no unexpected wait return values.
