# sources/security-integrity/audit-userspace/rules/30-ospp-v42.rules

Purpose: umbrella OSPP v4.2 audit policy profile supplementing the split create/modify/access/delete/permission/owner files. It targets account/group modification, special configuration utilities, session files, audit trail access, MAC policy, and privilege escalation helpers.

Important rules: 72 active rules. Keys include `user-modify`, `group-modify`, `special-config-changes`, `session`, `access-audit-trail`, `MAC-policy`, and `maybe-escalation`.

Control flow: intended to be installed with `10-base-config.rules`, `11-loginuid.rules`, and the split `30-ospp-v42-*` files. It uses b32/b64 pairs for paths and syscall filters.

State and persistence: kernel audit rule state after rules.d load.

Dependencies and integration: relies on auditctl path/dir/perm parsing, arch selectors, auid filters, and first-match ordering.

Risks and test signals: many path rules assume distribution-specific binaries such as `/usr/sbin/unix_chkpwd`, `/usr/bin/pkexec`, and `/usr/bin/systemd-run`. Test by `auditctl -R` on target distro and key-based ausearch checks for representative paths.
