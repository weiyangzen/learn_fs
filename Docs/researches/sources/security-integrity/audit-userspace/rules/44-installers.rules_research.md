# sources/security-integrity/audit-userspace/rules/44-installers.rules

Purpose: audits execution of common software installer/package tools.

Important rules: 14 b32/b64 path execution rules for `dnf-3`, `yum`, `pip`, `npm`, `cpan`, `gem`, and `luarocks`, key `software-installer`.

Control flow: path/perm execution filters.

State and persistence: kernel audit rules.

Dependencies and integration: assumes installer paths under `/usr/bin`; auditctl path and perm parsing.

Risks and test signals: misses tools at alternate paths or package managers not listed. Test by executing a listed installer and searching key `software-installer`.
