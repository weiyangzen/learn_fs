# sources/test-tools/liburing/test/eventfd-disable.c

Purpose: verifies runtime disable/enable of CQ eventfd notifications, including defer-taskrun mode. Important APIs are `io_uring_register_eventfd`, `io_uring_cq_eventfd_enabled`, `io_uring_cq_eventfd_toggle`, `eventfd`, eventfd `readv`, and NOP submissions.

Control flow: register eventfd, disable notifications, submit an eventfd read plus 63 NOPs and ensure only NOP CQEs arrive; re-enable, submit one NOP, and expect both NOP and eventfd read with value 1. State is eventfd counter and CQ notification flag. Risks are unavailable CQ flags, notifications firing while disabled, or not firing after re-enable.
