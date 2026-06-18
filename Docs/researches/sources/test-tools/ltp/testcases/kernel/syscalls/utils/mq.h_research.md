<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq.h

Purpose: common POSIX message queue setup/cleanup helper for LTP mqueue syscall tests. It creates unique blocking and nonblocking queue names, initializes shared message buffers, installs a SIGINT handler, and drains/unlinks queues during cleanup.

Important APIs/types/functions: globals `queue_name`, `queue_name_nonblock`, `smsg`, and `act` are shared with including tests, which are expected to define descriptors such as `fd_root`, `fd`, and `fd_nonblock`. `setup_common()` creates `/test_mqueue_<pid>` queues via `SAFE_MQ_OPEN`, opens `/` into `fd_root`, and fills `smsg` with deterministic bytes. `cleanup_common()` closes positive descriptors and `mq_unlink()`s both names. `cleanup_queue()` uses `mq_getattr()` and repeated `mq_receive()` to drain queued messages.

Control flow/state: setup is idempotent for the generated names because it calls cleanup before creating queues. Persistent state is kernel POSIX mqueue objects under names derived from PID; cleanup removes them even if prior test iterations left residue.

Dependencies/integration: depends on LTP safe wrappers, `tst_sig_proc.h`, and `tst_safe_posix_ipc.h`. Including tests must link against POSIX realtime/mqueue support as required by the LTP build rules.

Risks/test signals: descriptor-close guards use `> 0`, so descriptor 0 would not be closed, though these opens normally return higher values. Draining logs every message and treats `mq_getattr()` failure as `TBROK`; tests using this helper should verify queue attributes and cleanup noise when failures occur.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq.h -->
