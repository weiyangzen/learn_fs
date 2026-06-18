# sources/security-integrity/audit-userspace/rules/20-dont-audit.rules

Purpose: placeholder for early "do not audit" suppressions. All example rules are commented out.

Important rules: examples suppress cron SELinux subject events, chrony time-adjust syscalls, and `CRYPTO_KEY_USER`.

Control flow: because audit rules are first-match-wins, uncommented suppressions belong early in the rules order.

State and persistence: no effect as shipped because it has zero active rules.

Dependencies and integration: uses normal audit rule syntax if uncommented.

Risks and test signals: uncommenting broad excludes can hide important events. Verify with `auditctl -l` and event generation for the affected source.
