# sources/security-integrity/audit-userspace/rules/31-privileged.rules

Purpose: template for generating privileged command audit rules from setuid files and file capabilities.

Important rules: no active rules. Comments provide `find`, `awk`, and `filecap` pipelines that emit b64 rules with key `privileged`.

Control flow: site administrators generate concrete path rules and usually add b32 equivalents.

State and persistence: no effect as shipped.

Dependencies and integration: generated output uses standard auditctl path/perm/auid syntax.

Risks and test signals: stale generated lists miss newly installed privileged binaries; generated rules are distro/local-state dependent. Test by regenerating on the target system and executing a known privileged binary.
