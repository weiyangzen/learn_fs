# File Research: sources/os/bsd/freebsd-src/sys/sys/cpu.h

## Purpose
Declares CPU device ivars and the machine-independent cpufreq framework ABI.

## Main Elements
- CPU ivars expose `pcpu`, nominal MHz, and CPUID data.
- Inline helpers read CPU ivars from parent bus.
- `struct cf_setting` describes driver-provided frequency/voltage/power/latency settings.
- `struct cf_level` combines absolute and relative settings into exported CPU frequency levels.
- Cpufreq type flags distinguish absolute, relative, info-only, and uncached drivers.
- Priority constants arbitrate user, kernel, and emergency frequency requests.
- APIs: `cpufreq_register()`, `cpufreq_unregister()`, `cpufreq_settings_changed()`, `cpu_est_clockrate()`.
- Eventhandlers notify pre-change, post-change, and levels-changed listeners.

## Dependencies And Integration
Uses device/bus ivars, eventhandlers, TAILQ levels, and implementation in `kern_cpu.c`.

## Risk Notes
Frequency changes affect scheduling, thermal control, and power policy. Driver settings must use `CPUFREQ_VAL_UNKNOWN` for unknown fields and respect cpufreq method contracts.
