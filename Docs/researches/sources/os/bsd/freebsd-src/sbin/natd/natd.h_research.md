# File Research: sources/os/bsd/freebsd-src/sbin/natd/natd.h

## Summary
Shared declarations and constants for `natd`.

## Main Contents
- Defines `PIDFILE` as `/var/run/natd.pid`.
- Defines packet direction constants `INPUT`, `OUTPUT`, and `DONT_KNOW`.
- Defines shutdown delay bounds.
- Declares `Quit()`, `Warn()`, and `SendNeedFragIcmp()`.
- Declares global `struct libalias *mla`.

## Research Notes
The header exposes the global libalias handle so `icmp.c` can checksum and alias generated ICMP packets consistently with the active instance.
