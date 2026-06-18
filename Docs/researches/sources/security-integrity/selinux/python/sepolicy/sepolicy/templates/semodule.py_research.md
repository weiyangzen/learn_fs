# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/semodule.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/semodule.py

Purpose: smaller command-snippet templates for semodule-based installation steps.

Important APIs and control flow: exposes `compile` for `make -f /usr/share/selinux/devel/Makefile`, `restorecon` for relabeling generated file paths, and `tcp_ports`/`udp_ports` snippets that add generated port labels through `semanage port -a -t TEMPLATETYPE_port_t -p`.

State and persistence: rendered snippets build `.pp` modules and update SELinux labeling/port databases when executed.

Dependencies and integration points: used by policy generation code that assembles install instructions; depends on `make`, `semodule`, `restorecon`, and `semanage`.

Risks and test signals: assumes generated port additions do not already exist and that commands run with sufficient privilege. No direct tests cover idempotency or conflicts.
