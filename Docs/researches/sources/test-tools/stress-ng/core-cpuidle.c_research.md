# sources/test-tools/stress-ng/core-cpuidle.c

Purpose: discovers CPU idle C-states, samples residency counters, and reports per-stressor idle residency.

Important APIs and control flow: `stress_cpuidle_init` scans Linux `/sys/devices/system/cpu/cpu*/cpuidle/state*`, builds a sorted unique linked list, and inserts C0/BUSY if needed; begin/end readers aggregate per-state `time` counters and wall-time samples; `stress_cpuidle_dump` computes percentages per stressor instance and emits text/YAML; `stress_cpuidle_log_info` logs discovered states.

State and persistence: owns process-global linked list `cpu_cstate_list` and length; begin/end mutate caller stats. Reads sysfs only.

Dependencies and integration: depends on stressor stats structures, YAML logging, time helpers, and Linux cpuidle sysfs.

Risks and test signals: counter units/availability vary; CPU hotplug can change state sets after init; residency over 100% is clamped as inaccurate. Signals are discovered C-state logging, sane YAML output, and no leaks after `stress_cpuidle_free`.
