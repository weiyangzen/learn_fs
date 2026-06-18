# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/script.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/script.py

Purpose: shell script template fragments for building, installing, packaging, labeling, and configuring generated SELinux policy modules.

Important APIs and control flow: `compile` creates a generated shell script that locates its directory, supports `--update`, builds `.pp` modules via `/usr/share/selinux/devel/Makefile`, installs with `semodule -i`, handles optional RPM build, restorecon, port additions, user mappings, role/default-context changes, and admin transitions through appended command snippets. Separate constants provide RPM invocation, manpage generation, restorecon commands, TCP/UDP port semanage commands, SELinux user modifications, existing-user role changes, admin transition generation, and default context file fragments.

State and persistence: rendered scripts modify installed policy modules, file labels, semanage port/user/login databases, RPM build artifacts, and default context files when executed.

Dependencies and integration points: depends on shell, `semodule`, `semanage`, `restorecon`, `rpmbuild`, `sepolicy manpage`, and the SELinux devel Makefile.

Risks and test signals: generated scripts perform privileged policy installation and semanage changes; placeholder replacement must be exact. The script has multiple side effects and little validation beyond command failure. No direct tests target generated scripts.
