# sources/security-integrity/audit-userspace/docs/Makefile.am

Purpose: Automake manifest for audit-userspace manual pages and documentation tests.

Important variables and targets: `EXTRA_DIST=$(man_MANS)`, `dist_check_SCRIPTS=check-manpages.sh`, `TESTS=check-manpages.sh`, and a long `man_MANS` list covering libaudit, auparse, auplugin, auditd, auditctl, ausearch, aureport, augenrules, config files, and plugin man pages.

Control flow: Automake installs listed man pages and includes them in distribution archives. `make check` runs `check-manpages.sh` over manpage sources.

State and persistence: No runtime state; controls install/distribution artifacts and test registration.

Dependencies and integration: Integrates with automake, generated `docs/Makefile` from `configure.ac`, and manpage test script. The manpage list should track exported APIs and installed binaries.

Risks: Missing a new public function from `man_MANS` can ship undocumented APIs. Stale entries can break dist or install. The list is manually maintained and sensitive to filename spelling.

Test signals: `make -C docs check`, `make distcheck`, and package install file lists should confirm every listed page exists and formats cleanly.
