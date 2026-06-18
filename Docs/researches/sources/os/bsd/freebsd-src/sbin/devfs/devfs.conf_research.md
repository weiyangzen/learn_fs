# File Research: sources/os/bsd/freebsd-src/sbin/devfs/devfs.conf

## Purpose
Example `/etc/rc.d/devfs` device adjustment configuration.

## Main Elements
- Documents `link`, `perm`, and `own` examples.
- Shows sample aliases for `cd0`, permissions for `smb0`, speaker, and `bpf`.
- All example actions are commented.

## Dependencies And Integration
Read by rc scripts, not directly by `devfs.c`.
