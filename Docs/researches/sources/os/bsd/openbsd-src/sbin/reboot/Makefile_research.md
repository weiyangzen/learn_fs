# File Research: sources/os/bsd/openbsd-src/sbin/reboot/Makefile

## Purpose

Builds the `reboot` utility and installs `halt` as a hard link.

## Build Definition

The program is `reboot`, links with `libutil`, installs `reboot.8`, and creates a link from `reboot` to `halt`. Behavior differs based on invocation name.
