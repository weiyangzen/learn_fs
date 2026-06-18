# sources/user-network-fs/nfs-ganesha/src/include/gsh_recovery.h

Purpose: This header declares the recovery backend selector used by NFSv4 recovery configuration.

Important APIs/types/functions: `enum recovery_backend` lists filesystem, newer filesystem, RADOS key-value, newer RADOS, RADOS cluster, and disabled recovery modes. `RECOVERY_BACKEND_DEFAULT` is `RECOVERY_BACKEND_FS`.

Control flow: Config code stores one of these enum values in `nfs_version4_parameter_t`; recovery subsystems switch on it to choose the implementation for client/state recovery data.

State and persistence: The enum controls where persistent recovery records live. It does not itself store recovery state.

Dependencies and integration points: Included by `gsh_config.h` and any code interpreting NFSv4 recovery backend options.

Risks: Adding or reordering enum values can break config serialization or switch handling. `RECOVERY_BACKEND_NONE` disables recovery semantics and must be treated carefully around grace behavior.

Test signals: Verify config parsing for each backend, default behavior, switch exhaustiveness, and startup/restart behavior with filesystem and RADOS recovery modes.
