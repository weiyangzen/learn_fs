# File Research: sources/os/bsd/netbsd-src/sys/sys/pmf.h

## Purpose
Declares the NetBSD Power Management Framework event, suspend/resume, and device registration APIs.

## Main API
- Generic events: display, audio, lid, radio, power/speed/throttle, keyboard brightness event enum values.
- Qualifier type: `pmf_qual_t`.
- Qualifier constants: `PMF_Q_NONE`, `PMF_Q_SELF`, `PMF_Q_DRVCTL`.
- Framework calls: `pmf_init`, `pmf_event_inject`, `pmf_event_register`, `pmf_event_deregister`.
- Platform calls: `pmf_set_platform`, `pmf_get_platform`.
- System suspend/resume/shutdown: `pmf_system_resume`, `pmf_system_bus_resume`, `pmf_system_suspend`, `pmf_system_shutdown`.
- Device lifecycle: `pmf_device_register1`, `pmf_device_deregister`, `pmf_device_suspend`, `pmf_device_resume`, recursive/subtree helpers.
- Class registration: network, input, display.
- Inline qualifier helpers: `pmf_qual_suspension`, `pmf_qual_depth`, `pmf_qual_descend_ok`.

## Dependencies
Kernel/kmem-user sections use `sys/types.h` and `sys/device_if.h`.

## Risks and Notes
Suspend/resume depth is carried by qualifiers. Recursive operations should respect `pmf_qual_descend_ok`; drivers must register callbacks that tolerate being called during system-wide power transitions.
