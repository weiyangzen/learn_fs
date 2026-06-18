# sources/test-tools/fio/flow.c

Purpose: implements fio's `flow` option support, which throttles jobs sharing a `flow_id` so their issued I/O proportions track configured flow weights.

Important APIs/types/functions: internal `struct fio_flow` stores refs, id, intrusive list node, shared `flow_counter`, and `total_weight`. Exported functions are `flow_threshold_exceeded`, `flow_init_job`, `flow_exit_job`, `flow_init`, and `flow_exit`; internal helpers are `flow_get` and `flow_put`.

Control flow: `flow_init` allocates a shared flow list and a semaphore lock. `flow_init_job` obtains or creates a `fio_flow` for the job's `flow_id`, resets the job-local counter, and adds its weight to the group's total weight. During I/O selection, `flow_threshold_exceeded` compares the job's counter ratio against its weight ratio; if the job is ahead, it optionally quiesces and sleeps or quiesces for ZBD mode, then asks the caller to stall. Otherwise it atomically increments the shared and job-local counters. `flow_exit_job` subtracts the job's contribution, drops refs, and frees the flow when last user leaves.

State and persistence behavior: state is in fio shared allocations and atomic counters for the process lifetime. `flow_counter` starts at 1 to avoid division by zero and is expected to return to 1 when the last reference exits. There is no durable persistence.

Dependencies/integration: depends on `fio.h`, `fio_sem`, `smalloc`, `flist`, atomic helpers, `io_u_quiesce`, job options `flow`, `flow_id`, `flow_sleep`, and ZBD mode. It is called from job setup/teardown and I/O issue loops.

Risks and test signals: ratio math divides by atomically loaded counters and can be skewed by concurrent updates, but it is intended as proportional throttling rather than exact scheduling. Risks include missing `flow_init`, leaked refs, counter underflow in `flow_put`, and excessive stalls when flow weights or sleep settings are wrong. Tests should run mixed jobs with different weights, same/different `flow_id`, ZBD and non-ZBD modes, and teardown while counters are nonzero.
