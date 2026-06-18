# File Research: sources/virtualization/spdk/module/scheduler/gscheduler/gscheduler.c

Implements a simple governor-based scheduler that adjusts core frequency from load thresholds.

Key elements:
- Uses min, adjust, and max busy percentage thresholds.
- Selects `dpdk_governor` during init and clears governor on deinit.
- Calculates busy percentage from current busy/idle TSC.
- Considers SMT sibling busy percentage by taking the maximum among siblings.
- Sets core frequency min, down, up, or max based on load thresholds.
- Registers scheduler name `gscheduler`.

Dependencies:
- SPDK scheduler, governor, env, thread, and internal event APIs.

Research notes:
- This scheduler adjusts frequency only; it does not move threads between cores.
