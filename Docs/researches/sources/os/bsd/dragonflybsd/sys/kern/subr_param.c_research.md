# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_param.c

## Summary
Defines global kernel sizing parameters, boot-time tunable processing, and simple virtual-machine guest detection.

## Main Responsibilities
- Defines globals for `hz`, process/file limits, callouts, buffer counts, swap/bcache caps, and user address-space limits.
- `detect_virtual()` inspects SMBIOS loader environment strings for known hypervisors.
- `init_param1()` reads early tunables not scaled by memory.
- `init_param2()` computes memory-scaled limits such as `maxusers`, `maxproc`, `maxfiles`, and `ncallout`.
- Exposes `kern.vmm_guest`, `kern.maxssiz`, `kern.maxthrssiz`, and `kern.vmm_vendor`.

## Important Behavior
`maxusers` defaults from available physical/KVA MB when unset. `maxproc` is bounded by available KVA to avoid kmap exhaustion. `ncallout` is derived from process and file counts but capped at about five minutes of timer-wheel coverage.

## Risks
These globals influence broad kernel capacity and are initialized very early. Formula changes can shift process, descriptor, callout, and VM-space limits across the whole system. VM detection depends on exact SMBIOS strings.
