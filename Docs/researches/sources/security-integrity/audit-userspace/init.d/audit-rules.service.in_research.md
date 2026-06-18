# sources/security-integrity/audit-userspace/init.d/audit-rules.service.in

Purpose: systemd oneshot unit template that loads audit rules during boot or service start via `augenrules --load`.

Important fields: `ConditionKernelCommandLine=!audit=0` and `!audit=off`, `DefaultDependencies=no`, `After=local-fs.target systemd-tmpfiles-setup.service`, `Type=oneshot`, `ExecStart=@sbindir@/augenrules --load`, and optional commented `ExecStopPost=@sbindir@/auditctl -R @sysconfdir@/audit/audit-stop.rules`.

Control flow: systemd runs the unit once after local filesystems and tmpfiles setup, ensuring `/tmp` and rule files are available. It is wanted by `multi-user.target`.

State and persistence: Loads kernel audit rules and may optionally clear/disable rules on stop if the admin enables `ExecStopPost`.

Dependencies and integration: Template substitutions come from `init.d/Makefile.am`. It is wanted by `auditd.service` and integrates with `augenrules`, `auditctl`, `/etc/audit/rules.d`, and `/etc/audit/audit.rules`.

Risks: Security sandboxing is deliberately disabled because rule loading needs broad access. If rules are invalid, the unit can fail while `auditd.service` only has a weak `Wants` dependency. Optional stop behavior can remove audit coverage if enabled without policy intent.

Test signals: `systemd-analyze verify` on generated unit, boot/start ordering checks, `systemctl start audit-rules.service`, and inspection of loaded `auditctl -l` rules.
