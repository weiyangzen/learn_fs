# sources/test-tools/liburing/test/cq-peek-batch.c

Purpose: basic `io_uring_peek_batch_cqe` behavior test. Key APIs are `io_uring_prep_nop`, `io_uring_peek_batch_cqe`, `io_uring_cq_advance`, and user_data checks.

Control flow: assert empty batch, submit four NOPs and verify user_data 0-3, submit four more before advancing, advance first batch, and verify user_data 4-7. State is CQ readiness and advancement. Risk is incorrect order/count when new completions arrive before old ones are advanced.
