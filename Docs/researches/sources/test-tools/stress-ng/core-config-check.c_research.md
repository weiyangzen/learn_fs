# sources/test-tools/stress-ng/core-config-check.c

Purpose: runtime system-configuration sanity checks and performance warnings.

Important APIs and control flow: when metrics are enabled on Linux, reads scheduler autogroup, CPU boost/turbo, and per-CPU scaling governors; always checks memory/swap pressure and suggests `--oom-avoid` when low; on x86-64, validates `lahf_lm` CPUID by installing a SIGILL handler and executing `lahf`.

State and persistence: reads `/proc`/`/sys`, installs/restores a signal handler temporarily, and uses a volatile flag for SIGILL detection. It does not persist settings.

Dependencies and integration: depends on global `g_opt_flags`, memory limit helpers, signal helpers, x86 asm/cpu helpers, terminal ioctl, and logging.

Risks and test signals: warnings are advisory and Linux-specific; signal-handler probing must restore prior handler; reading governors can race CPU hotplug. Signals are expected notes under powersave/low-memory/disabled boost and no crash on Rosetta-like LAHF mismatch.
