<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-apparmor.c -->
# sources/test-tools/stress-ng/stress-apparmor.c

Purpose: `stress-apparmor.c` implements the `apparmor` stressor, which exercises AppArmor profile, feature, kernel-interface, and parser-corruption paths. It is a privileged OS/security stressor.

Important APIs/types/functions: the build requires AppArmor library/header support and `sys/select.h`; it includes generated `apparmor-data.h` policy bytes. `stress_apparmor_shared_info_t` contains lock pointers and a shared failure counter. `stress_apparmor_supported()` checks `CAP_MAC_ADMIN`, `aa_is_enabled()`, `aa_find_mountpoint()`, and readable `profiles`. `stress_apparmor_read()` and `stress_apparmor_dir()` read AppArmor sysfs/proc-style files. `apparmor_spawn()` forks synchronized child workers. Worker functions are `apparmor_stress_profiles()`, `apparmor_stress_features()`, `apparmor_stress_kernel_interface()`, and `apparmor_stress_corruption()`.

Control flow: `stress_apparmor()` allocates shared PID tracking, shared lock/counter memory, two policy-data buffers, and counter/failure locks. It spawns four children, one per AppArmor function, then starts all children after the normal sync barrier. The parent sleeps in `select(0, ...)` or `pause()` while locked bogo accounting says the stressor should continue. Shutdown sends `SIGALRM` to children through `stress_kill_and_wait_many()`.

State and persistence behavior: global process state includes `apparmor_path`, `apparmor_run`, `data_copy`, `data_prev`, and `stress_apparmor_shared_info`. Children may load, replace, and remove the generated profile, and the corruption worker preserves the last accepted corrupted policy in `data_prev`. The final return code fails if the shared failure counter is nonzero. AppArmor policy state is intended to be removed by the kernel-interface worker, but concurrent load/remove races are expected.

Dependencies and integration points: depends on libapparmor (`aa_kernel_interface_*`, `aa_is_enabled`, `aa_find_mountpoint`), stress-ng capabilities, locks, shared mmap, sync PID lists, scheduler helpers, parent-death alarms, and signal handlers. It registers `VERIFY_ALWAYS` and a supported callback; unavailable builds use `stress_unimplemented`.

Risks: this stressor mutates kernel security policy and requires elevated capability, so stale policy cleanup and concurrent EEXIST/ENOENT handling are important. Corruption tests intentionally feed malformed policy data and rely on expected `EPROTO`, `EPROTONOSUPPORT`, `ENOENT`, or `EEXIST`. Static variables inside corruption helpers are per-process but not reset between worker runs.

Test signals: skip behavior should be tested without capability, without AppArmor, without accessible `/sys/kernel/security/apparmor`, and without headers. Functional signals include zero shared failures, proper cleanup of loaded `/usr/bin/pulseaudio-eg` policy, child shutdown on `SIGALRM`, and bogo progress from all four worker lanes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-apparmor.c -->
