# sources/security-integrity/audit-userspace/rules/10-no-audit.rules

Purpose: performance-oriented policy that disables syscall auditing while leaving hardwired audit events.

Important commands: `-D` clears rules and `-a task,never` suppresses syscall auditing for all tasks.

Control flow: intended as an alternative to `10-base-config.rules` plus normal policy files.

State and persistence: persists through installed rules and kernel task filter state after load.

Dependencies and integration: parsed by auditctl rule setup and sent as a task filter rule.

Risks and test signals: creates major audit coverage gaps by design. Test signal is `auditctl -l` showing the task never rule and absence of syscall rules.
