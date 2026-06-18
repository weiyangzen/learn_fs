# File Research: sources/os/linux/linux/io_uring/io_uring.h

Main internal core header for io_uring. It defines setup/enter feature masks, ring layout/config structs, request return conventions, wait/defer structs, public core helper prototypes, and many hot inline helpers for CQE posting, SQ/CQ accounting, task refs, request cache allocation, and lock assertions.

Key contents:
- `IORING_FEAT_FLAGS`, `IORING_SETUP_FLAGS`, `IORING_ENTER_FLAGS`, and `SQE_VALID_FLAGS` centralize UAPI feature/flag validation.
- `IOU_COMPLETE`, `IOU_ISSUE_SKIP_COMPLETE`, `IOU_RETRY`, and `IOU_REQUEUE` define handler return protocol.
- `io_get_cqe_overflow()` and `io_fill_cqe_req()` implement cached CQE reservation, mixed/32-byte CQE advancement, copying request CQE payloads, and tracing.
- `io_req_set_res()`, `io_req_set_res32()`, and `req_set_fail()` standardize CQE result/failure state.
- `io_submit_flush_completions()`, `io_req_complete_defer()`, and `io_commit_cqring_flush()` are the fast-path deferred completion hooks.
- `io_ring_submit_lock/unlock()` abstract inline versus worker context locking.
- `io_sqring_entries()`, `io_sqring_full()`, and `io_should_wake()` handle shared ring state with RCU and acquire/release ordering.
- Request cache helpers use `ctx->submit_state.free_list` and refill through `__io_alloc_req_refill()`.

Dependencies: includes io-wq, alloc cache, task-work, slist, opcode definitions, io_uring types, and trace events.
