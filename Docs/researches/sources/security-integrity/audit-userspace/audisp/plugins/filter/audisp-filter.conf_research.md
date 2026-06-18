## sources/security-integrity/audit-userspace/audisp/plugins/filter/audisp-filter.conf

Purpose: default rule file for audisp-filter.

It contains comments documenting ausearch-expression syntax, allowlist/blocklist behavior, event-based matching, and intended chaining with downstream plugins, but no active rules. State is installed under `/etc/audit/audisp-filter.conf`. Dependencies are auparse expression parser. Risks are empty rule set semantics depending on selected mode, and users needing to understand event-level forwarding. Test signal is `audisp-filter --check` on this file.
