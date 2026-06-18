# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_fault.c

Read completely: 282 lines.

Implements the kernel fault-injection control device and API. The exported `fault_inject()` checks either a global fault configuration or the current LWP's specific-data configuration and returns true on every configured Nth call, with one-shot behavior after the first injected fault.

Control surface:
- `FAULT_IOC_ENABLE` supports `FAULT_MODE_NTH_ONESHOT` for global or per-LWP scope.
- `FAULT_IOC_DISABLE` turns off global or current-LWP injection.
- `FAULT_IOC_GETINFO` returns the number of injected faults for the chosen scope.
- Per-LWP state is allocated lazily through `lwp_setspecific()` and freed by the LWP-specific-data destructor.
- The module initializes the global mutex and LWP key, and refuses unload.

Concurrency and risks:
- Global enable/disable is serialized by `fault_global_lock`; fast-path reads use atomic loads.
- Per-LWP configuration is not globally locked, matching the LWP-specific-data ownership model.
- One-shot and counters are volatile/atomic enough for the intended debug use, but not a transactional policy interface.
