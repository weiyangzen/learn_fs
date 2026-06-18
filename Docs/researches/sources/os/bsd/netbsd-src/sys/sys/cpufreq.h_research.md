# File Research: sources/os/bsd/netbsd-src/sys/sys/cpufreq.h

Defines the CPU frequency state interface shared between kernel and ioctl-facing structures.

Key content:
- Limits: `CPUFREQ_NAME_MAX`, `CPUFREQ_STATE_MAX`, `CPUFREQ_LATENCY_MAX`.
- State markers: `CPUFREQ_STATE_ENABLED`, `CPUFREQ_STATE_DISABLED`.
- `struct cpufreq_state`: frequency in MHz, power in mW, latency in usec, index, reserved fields.
- `struct cpufreq`: name, state counts/target/current, reserved fields, CPU/backend index, plus kernel-only backend state and xcall callbacks.
- Kernel APIs to register/deregister, suspend/resume, get/set frequencies, and query states.

Important behavior:
- Kernel builds include `sys/xcall.h`.
- Non-kernel builds include `stdbool.h`.
