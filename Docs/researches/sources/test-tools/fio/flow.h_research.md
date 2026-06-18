# sources/test-tools/fio/flow.h

Purpose: public declaration for fio flow-control support.

Important APIs/types/functions: defines `FLOW_MAX_WEIGHT` as 1000 and declares `flow_threshold_exceeded`, `flow_init_job`, `flow_exit_job`, `flow_init`, and `flow_exit`.

Control flow: fio core initializes the subsystem once, initializes per-job flow state for jobs with `flow` weight, checks `flow_threshold_exceeded` during issue decisions, and tears down job/subsystem state at exit.

State and persistence behavior: the header exposes no state, but callers should treat flow state as process-lifetime shared scheduler state managed by `flow.c`.

Dependencies/integration: it requires `struct thread_data` from including context, normally through `fio.h`. It is included by `fio.h`, making flow checks available broadly.

Risks and test signals: changing `FLOW_MAX_WEIGHT` or function semantics affects option validation and runtime throttling. Test signals are compile coverage plus proportional throughput tests for weighted jobs.
