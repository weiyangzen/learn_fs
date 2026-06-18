# File Research: sources/virtualization/spdk/module/scheduler/dynamic/scheduler_dynamic.c

Implements SPDK's dynamic thread scheduler.

Key elements:
- Tracks per-core busy/idle TSC, thread count, and isolation state.
- Uses configurable thresholds: `load_limit`, `core_limit`, and `core_busy`.
- Optionally selects `dpdk_governor` during init.
- Moves idle threads to the main scheduling core.
- Moves active threads to cores that can fit their load while respecting thread cpumasks and isolated cores.
- Switches unused cores to interrupt mode and wakes/sleeps cores through governor frequency controls.
- Adjusts main-core frequency based on whether busy threads remain elsewhere.
- Exposes JSON scheduler options through `set_opts()` and `get_opts()`.
- Registers scheduler name `dynamic`.

Dependencies:
- SPDK env, thread, scheduler, internal event, logging, JSON, and USDT probe APIs.

Research notes:
- The algorithm updates estimated core load as it virtually moves threads so later placement decisions see the adjusted state.
