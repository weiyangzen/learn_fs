# File Research: sources/os/bsd/freebsd-src/sbin/devfs/devfs.rules

## Purpose
Default devfs rulesets for hiding/unhiding common devices, especially for jails.

## Main Elements
- `devfsrules_hide_all=1`: hide everything.
- `devfsrules_unhide_basic=2`: unhide null, zero, crypto, random, urandom.
- `devfsrules_unhide_login=3`: unhide pty/tty, ptmx, pts, fd, stdin/stdout/stderr.
- `devfsrules_jail=4`: include base sets and unhide fuse/zfs.
- `devfsrules_jail_vnet=5`: include jail sets and unhide pf.

## Dependencies And Integration
Installed under `/etc/defaults`. Lines are intended for expansion/application by rc scripts invoking `devfs`.
