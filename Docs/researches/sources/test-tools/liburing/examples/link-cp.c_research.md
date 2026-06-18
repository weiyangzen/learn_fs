# sources/test-tools/liburing/examples/link-cp.c

## sources/test-tools/liburing/examples/link-cp.c

Purpose: Basic file copy proof-of-concept using linked read/write SQEs.

Important APIs/types/functions: `struct io_data`, global `infd/outfd/inflight`; `queue_rw_pair`, `handle_cqe`, `copy_file`; `IOSQE_IO_LINK`; `io_uring_prep_readv`, `io_uring_prep_writev`.

Control flow: main opens files and initializes ring. `copy_file` queues read/write pairs while `inflight < QD`, submits, then waits when queue pressure is high. Each pair stores one shared data object; read SQE is linked to write SQE. Completion handler increments pair completion count, retries canceled linked pairs on `-ECANCELED`, frees data after both CQEs complete, and decrements inflight.

State and persistence: writes output file; heap chunk per copy segment.

Dependencies/integration: liburing linked SQE semantics, regular/block input size discovery.

Risks: explicitly lacks short read handling. If read returns short but not error, linked write may write stale/extra bytes. Retry on canceled pairs can duplicate work if not carefully reasoned. Global `inflight` tracks SQEs, not logical chunks, which can be confusing.

Test signals: successful copy can be externally compared; runtime prints CQE errors.
