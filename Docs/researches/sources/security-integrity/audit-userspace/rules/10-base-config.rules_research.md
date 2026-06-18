# sources/security-integrity/audit-userspace/rules/10-base-config.rules

Purpose: baseline rule file for systems that want syscall auditing. It deletes existing rules, sets backlog capacity, sets backlog wait time, and chooses audit failure mode.

Important commands: `-D`, `-b 8192`, `--backlog_wait_time 60000`, and `-f 1`.

Control flow: loaded by `auditctl -R` or augenrules in filename order; this file should precede policy files because it resets current rules.

State and persistence: persists only when installed in rules.d and loaded into the kernel audit subsystem. It changes kernel audit backlog/failure configuration.

Dependencies and integration: parsed by `auditctl.c` option handlers for delete-all, backlog, wait time, and failure mode.

Risks and test signals: `-D` removes existing rules, so ordering is critical. Test by loading on an audit-capable host and checking `auditctl -s`.
