# File Research: sources/os/bsd/openbsd-src/sbin/nfsd/Makefile

Purpose: Builds OpenBSD `nfsd`.

Build details:
- `PROG=nfsd`.
- Installs `nfsd.8`.
- Uses standard `<bsd.prog.mk>`.
- Explicitly clears `LDSTATIC` so `nfsd` is not built static by default.
