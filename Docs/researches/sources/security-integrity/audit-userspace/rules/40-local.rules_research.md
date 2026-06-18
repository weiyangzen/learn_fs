# sources/security-integrity/audit-userspace/rules/40-local.rules

Purpose: empty local customization anchor for site-specific watches after packaged policy rules.

Important rules: no active rules; comments show path and directory examples.

Control flow: filename positions local additions around the middle/end of the rule set.

State and persistence: no effect until edited locally.

Dependencies and integration: standard auditctl syntax.

Risks and test signals: packaged updates should preserve local intent only if admins manage this file appropriately. Test any added local rule with `auditctl -l` and event generation.
