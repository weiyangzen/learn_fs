# sources/test-tools/stress-ng/stress-rtc.c

Purpose: implements `rtc`, a Linux real-time-clock stressor that exercises `/dev/rtc`, `/sys/class/rtc/rtc0/*`, and `/proc/driver/rtc` read/ioctl interfaces.

Important APIs/types/functions: `stress_rtc_dev()` opens `/dev/rtc` and probes many RTC ioctls: time read/set echo, alarm read/set echo, wake alarm, AIE/UIE/PIE on/off, epoch, IRQ period, voltage-low, RTC params, select timeout, and illegal ioctl. `stress_rtc_sys()` reads standard sysfs RTC attributes. `stress_rtc_proc()` reads proc driver state. `stress_rtc_info` is `CLASS_OS`, `VERIFY_ALWAYS`.

Control flow: `stress_rtc()` synchronizes, then in each loop runs the device, sysfs, and proc probes while their respective paths remain viable. Missing paths disable that probe; if all are absent it skips with `EXIT_NO_RESOURCE`. Unexpected errors outside tolerated permission, busy, no-entry, interrupt, and unsupported cases fail the stressor. Successful full passes increment bogo.

State and persistence: persistent state is limited to static booleans suppressing repeated unavailable device opens and local probe-enable flags. The code attempts some setter ioctls only with values just read, but does not create files or durable repo state.

Dependencies and integration points: requires `linux/rtc.h`; optional branches use `select()`, newer RTC param structures, and many ioctl constants. It integrates with stress-ng file-read helpers, shim memset, sync, and diagnostics.

Risks and test signals: RTC devices often require privileges, may be busy, or may not exist in containers. Setter ioctls can be permission-sensitive. Signals are graceful skip on missing RTCs, bogo increments for successful probes, and failure only on unexpected kernel/user-space errors.
