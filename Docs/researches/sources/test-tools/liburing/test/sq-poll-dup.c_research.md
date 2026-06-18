# sources/test-tools/liburing/test/sq-poll-dup.c

Purpose: tests SQPOLL rings sharing a workqueue while duplicating and optionally closing the original ring fd, ensuring enter/submission still works through the duplicate.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `IORING_SETUP_ATTACH_WQ`, `IORING_FEAT_SQPOLL_NONFIXED`, `dup`, `close`, direct `O_DIRECT` reads, `io_uring_prep_read`, and multi-ring arrays.

Control flow: creates four SQPOLL rings, rings 1-3 attached to ring 0's workqueue, performs direct reads across all rings, duplicates ring 0 fd and optionally closes the original, then reads through attached rings and the duplicated original ring before/after idle sleep. `main()` runs three combinations of dup/close behavior.

State/persistence behavior: reads from a 128 MiB temporary or supplied file using aligned buffers. Ring fd ownership and shared SQ thread state are the main kernel state.

Dependencies/integration: requires SQPOLL, nonfixed SQPOLL feature, O_DIRECT-capable file/device, and sufficient permissions. Direct I/O unsupported or inaccessible paths skip.

Risks/test signals: failures include read CQE sizes not equal to 4096, broken ring fd replacement, SQPOLL idle wake issues, or shared workqueue teardown problems.
