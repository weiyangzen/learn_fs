# File Research: sources/os/bsd/openbsd-src/sbin/shutdown/Makefile

This Makefile builds the privileged OpenBSD `shutdown` utility.

Key settings:
- `PROG=shutdown`
- `MAN=shutdown.8`
- Installs as owner `root`, group `_shutdown`, mode `4550`.
- Includes `<bsd.prog.mk>`.

Integration:
- The setuid/setgid install mode is part of the utility’s privilege model.

Risk notes:
- Build/install metadata is security-relevant because this binary controls shutdown behavior.
