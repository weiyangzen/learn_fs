# sources/security-integrity/audit-userspace/rules/12-cont-fail.rules

Purpose: changes auditctl rules-file load behavior so syntax or unsupported-field errors do not stop immediate processing, but final exit reports failure.

Important command: `-c`.

Control flow: when encountered during `auditctl -R`, `opt_continue` sets `ignore=1` and `continue_error=1`; later errors keep processing and cause a nonzero final result.

State and persistence: process-local auditctl behavior only; no kernel rule state.

Dependencies and integration: meaningful only inside a rules file load path in `auditctl.c::fileopt`.

Risks and test signals: can leave partially loaded rules while still signaling failure. Test by loading a file containing `-c`, a bad rule, and a later valid rule.
