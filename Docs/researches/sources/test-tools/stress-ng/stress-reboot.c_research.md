# sources/test-tools/stress-ng/stress-reboot.c research

Purpose: implements `reboot`, a Linux OS stressor that exercises invalid and namespace-contained reboot syscall paths without intending to reboot the host.

Important APIs, types, and functions: constants mirror Linux reboot magic values and command codes. `boot_magic` includes valid secondary magic values plus intentionally invalid values. With `clone`, `reboot_clone_func()` runs in a new PID and mount namespace and calls `shim_reboot()` with `POWER_OFF` across magic variants, exiting with `errno`.

Control flow: `stress_reboot()` records whether the process has `CAP_SYS_BOOT`, allocates a clone stack if supported, synchronizes, then loops. It optionally clones a PID namespace child and validates its reboot errno. It then calls `shim_reboot()` with incorrect magic for restart and software suspend, expecting `EINVAL` for capable users or `EPERM`/`EINVAL` for non-capable users. Non-capable runs also iterate all magic values for poweroff and validate permission-style failures. Bogo increments per loop.

State and persistence: only transient child namespaces and stack memory are used. The stressor intentionally avoids valid host reboot calls; no persistent files are touched.

Dependencies and integration: Linux `__NR_reboot`, optional `clone` with `CLONE_NEWPID | CLONE_NEWNS`, stress-ng capability checks, stack alignment, wait helpers, and syscall shim. Classified as OS and `VERIFY_ALWAYS`.

Risks: capability and namespace semantics vary by container; a privileged namespace reboot may have special behavior. The safety contract depends on invalid magic for host-level calls and isolated namespace use for poweroff-like calls. Incorrect errno expectations can create false failures across kernels.

Test signals: no-resource stack allocation skip, namespace child errno failures, permission skip for capable-but-denied cases, invalid-magic errno validation, and bogo increments without host reboot.
