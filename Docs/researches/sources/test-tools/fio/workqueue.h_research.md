# sources/test-tools/fio/workqueue.h

Purpose: public interface and data structures for fio's generic submit workqueue.

Important APIs/types: `workqueue_work` embeds a list node. `submit_worker` stores thread, lock/cond, list, flags, index, sequence, parent queue, private pointer, and output routing. Function typedefs define callback contracts for work execution, pre-sleep flushing, worker allocation/free/init/exit, and accounting. `workqueue_ops` groups callbacks and nice value. `workqueue` stores worker array, locks/conds, max worker count, thread data, and scheduling fields.

Control flow/state: inline helpers invoke optional callbacks with safe defaults. `workqueue_exit_worker()` passes a temporary sum counter if the caller supplies none.

Dependencies/integration: includes pthreads, fio list/type headers, and forward declarations for `thread_data` and `sk_out`.

Risks/test signals: the header exposes internal structs, so callers can accidentally depend on flags and locking. Callback signatures must remain stable. Tests should compile at least one real workqueue user and verify optional callback omissions.
