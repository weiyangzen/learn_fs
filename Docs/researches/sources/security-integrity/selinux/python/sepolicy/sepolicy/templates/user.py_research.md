# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/user.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/user.py

Purpose: template fragments for SELinux user, role, transition, sudo, and admin policy generation.

Important APIs and control flow: type templates cover unprivileged login users, admin users, restricted users, restricted X users, existing users, and root/base users with generated tunables for reading/managing home content. Rule fragments include application role transitions, role changes, broad admin capabilities and dontaudits, user home read/manage tunables, admin-role transition, application admin integration, role allows, sudo role template, and `newrole` execution.

State and persistence: rendered into generated `.te` policy modules that alter SELinux users, roles, and role transition behavior.

Dependencies and integration points: depends on userdom, sudo, seutil, logging, kernel, domain, and application interface macros. Paired script templates update semanage user/login/default-context state.

Risks and test signals: admin fragments grant significant capabilities (`dac_override`, `dac_read_search`, `kill`, `sys_ptrace`, `sys_nice`) and broad home-management tunables. Generated user policy must be reviewed before enforcement. No direct tests validate role graph correctness.
