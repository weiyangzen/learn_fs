# sources/test-tools/liburing/test/wq-aff.c

Purpose: checks io-wq worker CPU affinity for SQPOLL rings. It verifies the SQPOLL thread and io-wq worker are pinned to expected CPUs when affinity is registered.

Important APIs/types/functions: `verify_comm`, `verify_affinity`, `test`, `test_invalid_cpu`, `io_uring_register_iowq_aff`, `io_uring_queue_init_params`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SQ_AFF`, `IOSQE_ASYNC`, `/proc/<pid>/comm`, `sched_getaffinity`, `CPU_SET`, and `CPU_COUNT`.

Control flow: main requires at least two CPUs. It first creates an SQPOLL ring with an invalid CPU id and expects `-EINVAL`, unless `-EPERM` requires skip. Then `test(1)` creates an SQPOLL ring pinned to CPU 1, registers io-wq affinity to CPU 0, submits an async pipe read to force an io-wq worker, sleeps briefly, and verifies expected kernel thread comm names and affinity masks based on current pid offsets.

State/persistence behavior: ring thread affinity and io-wq worker affinity are kernel thread state. No persistent files; `/proc` is read for verification.

Dependencies/integration: depends on predictable thread naming/pid adjacency (`iou-sqp-<pid>` and `iou-wrk-<pid>`), CPU affinity APIs, SQPOLL permissions, and at least two online CPUs.

Risks/test signals: fragile if kernel thread creation order changes. It skips when `/proc` names or permissions do not match. Failures include wrong affinity mask width, wrong CPU, invalid CPU accepted, or registration errors.
