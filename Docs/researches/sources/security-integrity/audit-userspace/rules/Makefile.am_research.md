# sources/security-integrity/audit-userspace/rules/Makefile.am

Purpose: Automake distribution/install fragment for packaged audit rules.

Important APIs/types: `EXTRA_DIST` lists all shipped `.rules` files plus `README-rules`; `rulesdir = $(datadir)/audit-rules`; `dist_rules_DATA = $(EXTRA_DIST)`.

Control flow: build-system only. Distribution and install targets copy the rule templates to the audit rules data directory.

State and persistence: affects installed package contents, not runtime state.

Dependencies and integration: integrated with Autotools packaging and depends on all listed files existing.

Risks and test signals: adding a rule file without updating this list omits it from distribution/install. Test with `make distcheck` or install tree inspection.
