# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/Makefile

## Purpose
Builds the FreeBSD `dhclient` program, script, manpages, and tests.

## Main Elements
- Installs `dhclient.conf`.
- Builds many ISC/OpenBSD-derived source files including parser, BPF, packet, options, dispatch, and privilege-separation code.
- Installs `dhclient-script`.
- Links `libutil`; conditionally links Casper/cap_syslog when dynamic root and Casper are enabled.
- Sets `NO_WCAST_ALIGN=yes` and enables tests subdirectory.

## Dependencies And Integration
Part of the `dhclient` package and used by `devd/dhclient.conf` link-up events.
