# File Research: sources/os/bsd/freebsd-src/sbin/devd/autofs.conf

## Purpose
Refreshes autofs caches on GEOM device events.

## Main Elements
- A `notify 100` rule matches `system=GEOM`, `subsystem=DEV`.
- Action runs `/usr/sbin/automount -c`.

## Dependencies And Integration
Installed when autofs is enabled. Supports media-style automount maps responding to device changes.
