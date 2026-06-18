## sources/test-tools/stress-ng/stress-varyload.c

Purpose: Implements `varyload`, coordinating multiple stressor instances to vary active CPU load over time and optionally apply scheduler policies.

Important APIs/types/functions: `stress_varyload_info`, init/deinit pipe handlers, `stress_varyload_set_sched`, `stress_varyload_waste_time`, `stress_varyload_by_type`, and `stress_varyload`; options select workload method, interval, scheduler, and load pattern.

Control flow: instance zero collects other instance PIDs via a pipe, then synchronizes all workers. Controller stops/continues peers according to brownian, saw-increase, saw-decrease, triangle, pulse, random, or all-rotating load patterns. Active intervals call `stress_workload_waste_time`; non-controller instances just run workload batches when continued.

State and persistence: global pipe fds live across stressor init/deinit; pattern state is static inside `stress_varyload_by_type`; PIDs and one shared workload buffer are transient.

Dependencies/integration: scheduler APIs (`sched_setscheduler`, optional deadline/ext policies), workload method table, mmap/madvise, pipe synchronization, signals.

Risks: depends on multi-instance coordination; scheduler changes may require privilege; SIGSTOP/SIGCONT control can leave peers stopped if cleanup fails, so final continue loop is important.

Test signals: `VERIFY_ALWAYS`; logs selected method/type/interval and bogo increments during workload time.
