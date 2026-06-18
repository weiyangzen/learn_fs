# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/unit_file.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/unit_file.py

Purpose: template fragments for systemd unit file labeling and management.

Important APIs and control flow: declares `TEMPLATETYPE_unit_file_t` with `systemd_unit_file`, leaves `te_rules` empty, defines `TEMPLATETYPE_systemctl` interface for systemctl execution, passwd-agent FIFO reads, reading the unit file, managing service permissions, and process pattern checks. Admin fragments include systemctl and service all-perms. File-context template labels a specific unit file.

State and persistence: rendered into policy and file-context outputs; generated policy controls systemd service management.

Dependencies and integration points: depends on systemd reference-policy interfaces (`systemd_exec_systemctl`, `systemd_read_fifo_file_passwd_run`) and service-class permissions.

Risks and test signals: service manage permissions can enable start/stop/reload operations and should be limited to intended admin domains. No direct tests cover generated unit-file policy.
