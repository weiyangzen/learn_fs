# sources/security-integrity/selinux/libselinux/src/checkAccess.c

Purpose: Provides high-level access checking APIs around the AVC and a compatibility password-access check.

Important APIs/types/functions: `selinux_check_access()` checks one permission by source/target context strings, class name, permission name, and auxiliary audit data. `selinux_check_passwd_access()` and `checkPasswdAccess()` delegate to `selinux_check_passwd_access_internal()`. A `pthread_once_t` initializes the AVC once.

Control flow: the first access check initializes SELinux state and opens the AVC if SELinux is enabled. If SELinux is disabled, access is allowed. Otherwise contexts are interned with `avc_context_to_sid()`, status updates are processed, class and permission strings are resolved, unknowns are allowed only when `security_deny_unknown() == 0`, and `avc_has_perm()` performs the decision and audit. Password access checks current previous context, computes access on the `passwd` class, and permits on permissive mode.

State and persistence: uses process-global once state, AVC cache, and current SELinux status. It does not persist policy changes.

Dependencies and integration: integrates public libselinux callers with AVC, status mapping, class/permission mapping, `getprevcon_raw()`, and enforcement-state reads.

Risks and test signals: unknown-class handling must preserve errno when denial is required. Tests should cover disabled SELinux, AVC init failure, unknown class/permission with deny_unknown both ways, permissive password access, and audit auxiliary data propagation.
