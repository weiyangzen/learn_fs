# sources/test-tools/liburing/test/sq-poll-share.c

Purpose: tests SQPOLL workqueue sharing across multiple rings under sustained direct read load.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `IORING_SETUP_ATTACH_WQ`, `IORING_FEAT_SQPOLL_NONFIXED`, `io_uring_prep_read`, `O_DIRECT`, aligned buffers, and four-ring fanout.

Control flow: creates or uses a 128 MiB file, opens it with direct I/O, initializes four SQPOLL rings with rings 1-3 attached to ring 0, then loops through file-sized work queuing 64 reads per ring and waiting for each completion to return 4096 bytes.

State/persistence behavior: temporary read file is unlinked after open when created internally. Ring workqueue sharing and in-flight read state are the focus.

Dependencies/integration: requires SQPOLL, nonfixed SQPOLL feature, O_DIRECT support, and access to the test file/device.

Risks/test signals: detects sharing setup failures, read completion errors, wrong byte counts, and SQPOLL wake/completion issues under multi-ring load.
