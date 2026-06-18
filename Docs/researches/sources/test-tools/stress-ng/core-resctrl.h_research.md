# sources/test-tools/stress-ng/core-resctrl.h

Purpose: declares the public resctrl lifecycle used by option parsing and stressor process startup.

Important APIs/types/functions: `stress_resctrl_parse` parses the raw option string and returns failure for invalid syntax. `stress_resctrl_set` assigns a stressor name/instance/PID to its configured partition. `stress_resctrl_init` prepares the resctrl filesystem state after parsing. `stress_resctrl_deinit` tears it down and frees parser state.

Control flow: the header itself has no logic. The parse/init/set/deinit sequence is the intended lifecycle; calling `set` before parse/init is harmless in unsupported/no-config builds but cannot apply partitions.

State and persistence: all state is private to the implementation. External callers only pass the option string and per-process identity.

Dependencies/integration: relies on stress-ng-wide definitions for `uint32_t`, `pid_t`, and `WARN_UNUSED`. Integrated by main option handling and child stressor startup.

Risks: callers must not assume resctrl is available just because parsing succeeded; unsupported builds accept calls but log that settings are ignored. The option buffer is not promised immutable by implementation, so callers should treat parse input as consumed.

Test signals: compile on unsupported platforms, parse invalid strings, and verify the public lifecycle does not crash when no resctrls were configured.
