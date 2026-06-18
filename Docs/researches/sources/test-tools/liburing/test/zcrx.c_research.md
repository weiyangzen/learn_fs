# sources/test-tools/liburing/test/zcrx.c

Purpose: comprehensive zero-copy receive test suite for io_uring ZCRX registration, refill queues, nodev receive, import/export clone, invalid parameter handling, buffer return/flush, and abnormal teardown paths.

Important APIs/types/functions: `struct zcrx_reg`, `struct t_executor`, `write_ro_params`, `submit_and_wait_one`, `test_io_uring_prep_zcrx`, `query_zcrx`, `default_reg`, `try_register_zcrx`, `clone_zcrx`, `test_register_basic`, `test_rq`, `test_area`, `test_ro_params`, `test_invalid_rx_page`, `prep_server`, `return_buffer`, `transfer_bytes`, `test_invalid_recv`, `test_exit_with_inflight`, `test_zcrx_invalid_clone`, `test_zcrx_clone`, `test_rq_flush`, `test_recv`, `test_abnormal_exit`, `test_invalid_rq_pointers`, `test_invalid_rqes`, `test_area_ro`, `run_tests`, `io_uring_register_ifq`, `IORING_OP_RECV_ZC`, and `IORING_REGISTER_ZCRX_CTRL`.

Control flow: main queries ZCRX support and nodev registration flags, allocates default RQ/area/read-only parameter memory, then runs a sequence of registration and I/O tests. Early tests validate basic registration, invalid refill queue descriptors, invalid area descriptors, read-only parameter memory, read-only area memory, and invalid receive page lengths. Runtime tests register a nodev IFQ over a socket pair, test invalid receive fds/zcrx ids, exit with inflight receive, optionally export/import ZCRX state, flush refill queues, inject invalid refill queue pointers/RQEs, transfer patterned bytes with and without returning buffers, and exit abnormally across direct/io-wq and pinned/unpinned ZCRX cases.

State/persistence behavior: state is ring registration state, user-provided refill queue memory, registered receive area tokens, socket-pair data flow, exported ZCRX file descriptors, and memory protection for negative tests. No persistent filesystem artifacts.

Dependencies/integration: requires kernel ZCRX query/register support, `ZCRX_REG_NODEV`, CQE32/defer-taskrun/single-issuer/submits-all ring flags, socket pairs, mmap/mprotect/madvise, optional huge pages, and potentially `NET_ADMIN` capability.

Risks/test signals: skips when ZCRX or nodev mode is unsupported, or when registration returns `-EPERM`. Failures include invalid registration accepted, expected import/export errors missing, pattern mismatch in zero-copy payload, missing final non-more CQE, inability to return/flush buffers, or crashes during abnormal teardown. The setup maps `def_area_mem` twice, so memory accounting should be reviewed if extending this test.
