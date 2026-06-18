# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/sched.h

Purpose: Xen public scheduler-operation ABI. It defines `HYPERVISOR_sched_op` command numbers and payloads for yield, block, shutdown, event-channel polling, remote shutdown, shutdown code latching, and watchdog management.

Key interfaces:
- `sched_shutdown`, `sched_poll`, `sched_remote_shutdown`, `sched_watchdog`.
- Shutdown reasons: poweroff, reboot, suspend, crash, watchdog.

Integration notes: Includes `event_channel.h`. 9front Xen code uses `SCHEDOP_yield`, `SCHEDOP_block`, and `SCHEDOP_shutdown` wrappers in `xensystem.c`.

Risk/attention points: `SCHEDOP_shutdown` suspend has special extra-argument semantics; simple wrappers must not assume all shutdown reasons are identical.
