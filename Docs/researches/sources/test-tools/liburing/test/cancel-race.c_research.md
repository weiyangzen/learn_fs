# sources/test-tools/liburing/test/cancel-race.c

Purpose: stresses races between poll/read completion and async cancel. Important APIs are `io_uring_prep_poll_add`, `io_uring_prep_read`, `io_uring_prep_cancel64`, `IORING_ASYNC_CANCEL_ANY`, pthreads, pipes, and encoded user_data sequence/type values.

Control flow: repeat 10,000 poll+cancel pairs, then 10,000 read+cancel pairs, then run a concurrent cancel thread while another ring submits polls. State is in-flight operation identity and cancellation results. Test signals are exactly expected CQEs with allowed result codes; risks include hangs, lost completions, duplicate completion/cancel accounting, and unsupported cancellation.
