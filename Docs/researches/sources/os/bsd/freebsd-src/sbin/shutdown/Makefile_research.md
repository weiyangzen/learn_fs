# File Research: sources/os/bsd/freebsd-src/sbin/shutdown/Makefile

## Summary
Builds the `shutdown` runtime utility and installs `poweroff` as a hardlink/alias.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=shutdown` and `shutdown.8`.
- Links `${BINDIR}/poweroff` to `shutdown`.
- Adds manual alias `shutdown.8 poweroff.8`.
- Installs as root/operator with mode `4554`.

## Dependencies And Integration
Uses `bsd.prog.mk`; install mode supports privileged shutdown behavior for operator-group users.
