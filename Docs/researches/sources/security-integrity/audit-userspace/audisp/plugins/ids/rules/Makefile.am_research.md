# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/Makefile.am

Purpose: packages the IDS audit rule files for installation.

Important APIs and data: sets `EXTRA_DIST` and `dist_rules_DATA` to the four `25-*.rules` files; installs them under `$(datadir)/audit-rules/ids-rules`.

Control flow: automake uses these variables during dist and install targets.

State and persistence: no runtime state; controls distribution/install artifacts.

Dependencies and integration: integrates with the audit userspace build system and rule deployment location.

Risks: adding a new rule file without updating `EXTRA_DIST` leaves it out of packaged installs.

Test signals: `make distcheck` and install tree inspection should verify all four rules are present.
