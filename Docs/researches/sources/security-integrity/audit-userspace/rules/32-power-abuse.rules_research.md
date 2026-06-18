# sources/security-integrity/audit-userspace/rules/32-power-abuse.rules

Purpose: detects root browsing user home directories when the login audit uid belongs to a normal user.

Important rule: `-a always,exit -F dir=/home -F uid=0 -F auid>=1000 -F auid!=unset -C auid!=obj_uid -F key=power-abuse`.

Control flow: one exit filter using inter-field comparison.

State and persistence: kernel audit rule state.

Dependencies and integration: requires audit interfield comparison parsing via `audit_rule_interfield_comp_data`.

Risks and test signals: can be noisy for legitimate support/admin work and may miss non-`/home` user directories. Test by root accessing another user's home and searching `power-abuse`.
