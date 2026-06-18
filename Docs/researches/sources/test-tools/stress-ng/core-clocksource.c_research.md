# sources/test-tools/stress-ng/core-clocksource.c

Purpose: warns once when Linux is using HPET clocksource because it may distort benchmarking.

Important APIs and control flow: `stress_clocksource_check` scans `/sys/devices/system/clocksource/clocksource*/current_clocksource`, lowercases contents, and logs a warning if the value starts with `hpet`; a static `warned` latch prevents repeated warnings.

State and persistence: process-local one-time warning flag; reads sysfs but does not write it.

Dependencies and integration: uses directory traversal, `stress_fs_file_read`, and logging; called from runtime configuration/performance checks.

Risks and test signals: assumes sysfs clocksource layout; warning can be skipped after first detection. Signal is a single warning on HPET systems and silence otherwise.
