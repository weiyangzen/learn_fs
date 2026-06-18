# sources/test-tools/fio/pcbuf.h

Purpose: header-only two-phase circular buffer for producer/consumer separation with explicit commit.

Important APIs/types: `struct pc_buf` tracks `commit_head`, `staging_head`, `read_tail`, `capacity`, and a flexible `uint64_t buffer[]`. Inline APIs include `pcb_alloc()`, `pcb_is_empty()`, `pcb_is_full()`, `pcb_push_staged()`, `pcb_commit()`, `pcb_pop()`, `pcb_print_committed()`, `pcb_print_staged()`, `pcb_committed_size()`, `pcb_staged_size()`, and `pcb_space_available()`.

Control flow: producers stage items by writing at `staging_head`; consumers only see data up to `commit_head`. `pcb_commit()` publishes all staged entries by moving `commit_head` to `staging_head`. One slot is reserved so full and empty states are distinguishable.

State and persistence: all state is in the allocated buffer object; no synchronization primitives are included. `pcb_alloc()` uses `malloc()` and leaves freeing to the caller.

Dependencies and integration: generic utility header using standard C headers; useful where fio needs staged visibility of batches without a separate implementation file.

Risks: not thread-safe without external synchronization or memory barriers. `capacity` must be greater than one; zero capacity causes modulo-by-zero and one capacity leaves no usable slots. Allocation size can overflow for huge capacities.

Test signals: staged vs committed visibility, wraparound, full/empty detection, capacity edge cases, and concurrent usage only with explicit locking tests.
