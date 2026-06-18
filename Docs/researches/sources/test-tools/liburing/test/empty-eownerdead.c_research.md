# sources/test-tools/liburing/test/empty-eownerdead.c

Purpose: regression test that empty `io_uring_enter` on SQPOLL does not fail with `EOWNERDEAD`. Important APIs are `IORING_SETUP_SQPOLL`, `t_create_ring_params`, and raw `__sys_io_uring_enter`.

Control flow: create a one-entry SQPOLL ring, call enter with zero submit and zero wait, and fail on any negative result with special diagnostic for `EOWNERDEAD`. State is SQPOLL ring/thread state only. Risk is old-kernel empty-enter failure behavior.
