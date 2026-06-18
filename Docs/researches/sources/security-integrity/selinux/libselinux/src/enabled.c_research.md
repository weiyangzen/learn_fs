# sources/security-integrity/selinux/libselinux/src/enabled.c

Purpose: Reports whether SELinux and MLS are enabled.

Important APIs/types/functions: `is_selinux_enabled()` checks discovered mount/config state, using Android-specific logic that only requires `selinux_mnt`. `is_selinux_mls_enabled()` reads `selinux_mnt/mls` and returns true only when content is exactly `"1"`.

Control flow: enablement is based on constructor-initialized globals from `init.c`. MLS read retries no EINTR loop around open but does loop read until not interrupted.

State and persistence: reads process-global mount/config discovery and kernel MLS state.

Dependencies and integration: used by high-level access checks and callers deciding whether to perform SELinux work.

Risks and test signals: non-Android builds require both mount and config presence, which can differ in containers. Tests should cover Android/non-Android behavior, missing mount, malformed MLS content, and read interruption.
