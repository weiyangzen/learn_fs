# sources/test-tools/stress-ng/core-cpu-freq.c

Purpose: obtains average/min/max CPU frequency in GHz across supported platforms.

Important APIs and control flow: Linux scans `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq` and converts kHz to GHz; FreeBSD reads `dev.cpu.N.freq`; Apple reads `hw.cpufrequency`; OpenBSD reads `HW_CPUSPEED`; unsupported platforms zero all outputs.

State and persistence: reads kernel/sysctl state only.

Dependencies and integration: uses dirent scanning, sysctl helpers, CPU count helpers, and conversion constants.

Risks and test signals: current frequency can be unavailable, stale, or per-policy rather than per-core; Linux frees scan entries while iterating and handles no data by zeroing. Signals are nonzero plausible GHz on systems exposing frequency and zeros otherwise.
