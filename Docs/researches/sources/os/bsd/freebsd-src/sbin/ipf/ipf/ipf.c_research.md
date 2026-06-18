# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipf.c

## Purpose
Main command-line utility for controlling IPFilter filter rules and global filter state.

## Main Elements
- Parses options for IPv4/IPv6 mode, active/inactive list selection, debug, dry-run, load file, flush, packet logging, expression flush matching, auth device, remove mode, swap active lists, tuning, verbosity, version, sync, zero rule stats, and zero global stats.
- `procfile()` opens the device, initializes parser state, and loads rules through `ipf_parsefile()`.
- `ipf_interceptadd()` optionally emits compiled C then submits rules with `ipf_addrule()`.
- `flushfilter()` flushes filter rules or state entries, optionally by parsed expression.
- `packetlogon()` toggles pass/block/nomatch filter log flags and NAT/state logging.
- `showversion()` prints user/kernel version, running status, flags, default policy, active list, and feature mask.
- `zerostats()` clears and prints filter statistics.

## Dependencies And Integration
Uses `/dev/ipl`-style device names from IPFilter headers, parser helpers from common code, and many IPFilter ioctls such as `SIOCFRENB`, `SIOCIPFFL`, `SIOCSWAPA`, `SIOCFRSYN`, `SIOCFRZST`, and `SIOCGETFS`.

## Risk Notes
Most operations mutate live firewall state. Dry-run mode avoids device opens, but option combinations strongly affect whether rules are added, removed, inserted, flushed, or just printed.
