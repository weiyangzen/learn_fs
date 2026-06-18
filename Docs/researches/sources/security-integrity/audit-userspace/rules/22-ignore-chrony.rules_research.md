# sources/security-integrity/audit-userspace/rules/22-ignore-chrony.rules

Purpose: suppresses chrony-generated `adjtimex` time-change events for both b64 and b32 architectures.

Important rules: two `never,exit` rules with `auid=unset`, `uid=chrony`, and `subj_type=chronyd_t`.

Control flow: should load before time-change auditing rules so first-match suppression wins.

State and persistence: kernel audit filter state.

Dependencies and integration: assumes chrony user and SELinux type names match the target system.

Risks and test signals: may suppress malicious activity if chrony identity is compromised or labels differ. Validate by observing absence of chrony time-change records while other time-change records remain.
