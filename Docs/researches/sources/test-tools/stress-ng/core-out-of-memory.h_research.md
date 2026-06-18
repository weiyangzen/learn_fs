# sources/test-tools/stress-ng/core-out-of-memory.h

Purpose: declares OOM adjustment and OOM-tolerant child execution helpers.

Important APIs/types: `stress_oomable_child_func_t`, `stress_process_oomed`, `stress_set_oom_adjustment`, and `stress_oomable_child`.

Control flow: header only establishes that wrapped callbacks receive `stress_args_t *` and opaque context and return an exit status.

State/persistence: no header state; declared functions manipulate process OOM settings and child lifecycle.

Dependencies/integration: includes `stress-ng.h` for `stress_args_t`, `pid_t`, bool, and wrapper flags supplied elsewhere.

Risks: callbacks must be safe to run in a forked child and must not rely on parent-only state after fork.

Test signals: compile stressors using the callback type and verify wrapper flags are passed consistently.
