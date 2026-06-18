# File Research: sources/os/bsd/freebsd-src/sbin/resolvconf/Makefile

Build/install file for imported openresolv scripts and support files.

Key elements:
- Uses `${SRCTOP}/contrib/openresolv` as source path.
- Installs script `resolvconf`.
- Installs support files `libc`, `dnsmasq`, `named`, `pdnsd`, `pdns_recursor`, and `unbound` under `/libexec/resolvconf`.
- Generates scripts/files/manpages from `.in` templates with `sed` substitutions for sysconf, libexec, var, rc, sbin paths, restart command, and FreeBSD VPN interface pattern handling.
- Defines restart command through `/usr/sbin/service ... onestatus && ... restart`.

Dependencies:
- `bsd.prog.mk`, openresolv template files, and FreeBSD service layout.
