# File Research: sources/os/bsd/freebsd-src/sbin/devd/nvmf.conf

## Purpose
Reconnects NVMe over Fabrics host controllers when requested.

## Main Elements
- Matches `system=nvme`, `subsystem=controller`, `type=RECONNECT`.
- Runs `nvmecontrol reconnect $name`.

## Dependencies And Integration
Installed in the NVMe tools package group.
