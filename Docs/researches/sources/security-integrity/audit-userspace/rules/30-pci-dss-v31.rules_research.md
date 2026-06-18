# sources/security-integrity/audit-userspace/rules/30-pci-dss-v31.rules

Purpose: PCI DSS v3.1-oriented audit policy profile covering cardholder data access placeholders, privileged configuration changes, audit trail access, account changes, system objects, time changes, and audit log modification.

Important rules: 46 active rules. Keys include `10.2.1-cardholder-access`, `10.2.2-priv-config-changes`, `10.2.3-access-audit-trail`, `10.2.5.*`, `10.2.7-system-objects`, `10.4.2b-time-change`, and `10.5.5-*`.

Control flow: loaded as a rules.d profile after base configuration. Some sample paths such as `path-to-db` and `path-to-log` are placeholders requiring site customization.

State and persistence: kernel audit rules when loaded.

Dependencies and integration: standard auditctl parser; uses b32/b64 arch pairs, path/dir filters, and syscall filters.

Risks and test signals: placeholder paths must be replaced or rules will not provide intended compliance evidence. Test with `auditctl -R` and targeted operations for time change, audit tool execution, account file changes, and configured data paths.
