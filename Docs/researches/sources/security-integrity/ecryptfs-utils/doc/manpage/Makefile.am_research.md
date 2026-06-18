# sources/security-integrity/ecryptfs-utils/doc/manpage/Makefile.am

Purpose: installs and distributes ecryptfs-utils manual pages.

Important APIs/targets: `dist_man_MANS` lists section 1, 7, and 8 man pages for mount helpers, utilities, PAM integration, setup/recovery, passphrase wrapping, and stat/verify commands.

Control flow/state: Automake handles install and distribution of listed man pages.

Dependencies/integration: configured as `doc/manpage/Makefile` and recursed from `doc/Makefile.am`.

Risks: man page list must stay synchronized with installed utilities; stale entries break dist/install.

Test signals: `make install`, `make distcheck`, and packaging file checks.
