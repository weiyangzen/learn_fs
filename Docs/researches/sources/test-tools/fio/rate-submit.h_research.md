# sources/test-tools/fio/rate-submit.h

Purpose: declarations for rated/offloaded IO submission lifecycle.

Important APIs/types: declares `rate_submit_init(struct thread_data *, struct sk_out *)` and `rate_submit_exit(struct thread_data *)`.

Control flow and state: no implementation; functions operate on fio thread data and socket output context.

Dependencies and integration: paired with `rate-submit.c`; requires broader fio declarations for `struct thread_data` and `struct sk_out`.

Risks: callers must only expect workqueue setup when offload mode is active; init returns zero for other modes.

Test signals: compile and offload/non-offload initialization behavior.
