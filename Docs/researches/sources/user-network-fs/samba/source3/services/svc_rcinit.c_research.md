# sources/user-network-fs/samba/source3/services/svc_rcinit.c

Purpose: legacy/disabled Service Control Manager bridge for Unix rc/init scripts.

Important functions and APIs: `rcinit_stop()`, `rcinit_start()`, and `rcinit_status()` contain disabled `#if 0` implementations that would construct commands under `${MODULESDIR}/svcctl/<service>` and run them as root via `smbrun`. In compiled code, they return `WERR_ACCESS_DENIED` unless the disabled command path is re-enabled and succeeds. Exports `SERVICE_CONTROL_OPS rcinit_svc_ops`.

Control flow: current compiled control flow is denial-only. The disabled code shows the intended start/stop/status sequence, root transition, command execution, and `SERVICE_STATUS` population.

State and persistence: no runtime state changes in the active build. If re-enabled, it would execute external scripts and reflect their exit codes as service state.

Dependencies and integration: included in the svcctl operations ecosystem through `services.h`. The disabled path references `get_dyn_MODULESDIR`, `SVCCTL_SCRIPT_DIR`, `become_root`, `smbrun`, and service-control status constants.

Risks and test signals: the comments explicitly cite security concerns and unknown field use as the reason for disabling. Re-enabling would create a high-risk root command-execution surface. Current test signal is that start/stop/status through this backend are denied.
