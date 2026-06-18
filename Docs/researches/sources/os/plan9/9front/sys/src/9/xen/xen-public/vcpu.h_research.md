# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/vcpu.h

Purpose: Xen public VCPU operation ABI. It defines operations for VCPU initialization, up/down, runstate queries, shared runstate/time registration, VCPU timers, NMI sending, and physical ID lookup.

Key interfaces:
- `VCPUOP_initialise`, `VCPUOP_up`, `VCPUOP_down`, `VCPUOP_is_up`.
- `vcpu_runstate_info`, `vcpu_register_runstate_memory_area`.
- `vcpu_set_periodic_timer`, `vcpu_set_singleshot_timer`.
- `vcpu_register_vcpu_info`, `vcpu_get_physid`, `vcpu_register_time_memory_area`.

Integration notes: Depends on `xen.h`. 9front’s Xen timer code reads the shared `vcpu_time_info` through `shared_info` rather than using the registration op.

Risk/attention points: The comments document important hotplug race and memory-reference caveats; VCPU down is generally asynchronous unless self-invoked.
