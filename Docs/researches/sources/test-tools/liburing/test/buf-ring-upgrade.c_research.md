# sources/test-tools/liburing/test/buf-ring-upgrade.c

Purpose: race/regression test for upgrading a legacy provided-buffer group into a ring-provided group after the legacy buffer is drained. Important APIs are `io_uring_prep_provide_buffers`, raw `IORING_REGISTER_PBUF_RING`, selected-buffer `recv`, `socketpair`, forked sender/registrar loops, shared `mmap`, and alarm timeout.

Control flow: provide one legacy buffer, create a candidate pbuf ring, fork a sender and a registrar racing registration, and repeatedly issue selected-buffer receives until registration succeeds, unsupported state is detected, or iteration limits/timeout end. State is shared flags plus ring buffer group state. Risks are scheduling sensitivity, weak assertions, hangs, crashes, and unexpected registration errors.
