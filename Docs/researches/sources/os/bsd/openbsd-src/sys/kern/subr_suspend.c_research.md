# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_suspend.c

Coordinates system suspend, hibernate, resume, and wakeup-device accounting. It is a compact but system-wide control path that quiesces devices, filesystems, buffer queues, CPUs, timers, entropy, sensors, profiling, and optional hibernate state before entering platform sleep.

`device_register_wakeup()` increments the global active wakeup-device count. `sleep_state()` is the main suspend/hibernate state machine. It rejects suspend when no wakeup devices exist, asks platform code to show/validate sleep state, suspends wsdisplay when present, stops periodic RTC updates, and for hibernate discards buffer cache/page daemon state and allocates hibernate memory.

Before sleeping, it quiesces sensors and all devices with `DVACT_QUIESCE`, stalls VFS via `vfs_stall(curproc, 1)`, quiesces softraid when configured, quiesces buffer queues, stops secondary CPUs, disables kernel profiling execution state, and performs MP sleep preparation. For hibernate it again trims dirty memory before snapshotting.

The critical suspend section raises IPL, disables interrupts, marks `cold = 2` so other code uses delays instead of sleeps, enables wakeup interrupts, sends `DVACT_SUSPEND`, suspends randomness, calls platform `sleep_setstate()`, optionally powers down devices for regular suspend via `DVACT_POWERDOWN`, drops performance to minimum, and invokes `gosleep()`.

Resume unwinds through labeled failure/resume paths: device resume, interrupt/wakeup restoration, time and clock interrupt reinitialization, `resume_time` update, platform `sleep_resume()`, randomness resume with hibernate entropy if available, MP resume, profiling restore, secondary CPU restart, VFS unstalls, buffer queues restart, device wakeup, sensor restart, hibernate memory cleanup, periodic RTC restart, wsdisplay resume, `sys_sync()`, and performance-level restoration. `suspend_finish()` can request another sleep loop.

`resuming()` reports whether current uptime is within ten seconds after the latest resume.

Filesystem relevance: `vfs_stall()`, `bufq_quiesce()`, `bufq_restart()`, hibernate buffer-cache suspension/resume, and final `sys_sync()` make this important for filesystem consistency during suspend/hibernate. It explicitly prevents normal filesystem progress while storage/device state is unstable.
