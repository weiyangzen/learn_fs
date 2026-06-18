# sources/security-integrity/audit-userspace/rules/30-stig.rules

Purpose: STIG-oriented audit profile covering time changes, identity files, locale/network identity files, MAC policy, login/session files, permission changes, failed access, mounts, deletes, sudo configuration, and escalation helpers.

Important rules: 52 active rules. Keys include `time-change`, `identity`, `system-locale`, `MAC-policy`, `logins`, `session`, `perm_mod`, `access`, `export`, `delete`, `actions`, and `maybe-escalation`.

Control flow: intended with `10-base-config.rules` and `99-finalize.rules`; comments describe assumptions about UID_MIN, root login, and possible local narrowing.

State and persistence: kernel audit rules after load.

Dependencies and integration: parsed by auditctl and relies on path existence/meaning across distributions.

Risks and test signals: broad `dir=/etc` and access rules can be noisy. Some optional login/session watches are commented. Test with representative file changes and check ausearch keys.
