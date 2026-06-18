# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acctctl.h

## Purpose

`acctctl.h` defines the `acctctl()` extended accounting control interface and kernel state for per-zone exacct settings.

## User ABI

Mode bits select process, task, flow, or network accounting. Option bits select file get/set, resource get/set, and state get/set operations. Resource IDs enumerate recordable fields for each accounting class, including process IDs, users, projects, CPU/time, zones, memory, flow addresses/ports/protocols, and network traffic counters.

`ac_res_t` carries one resource ID and enabled/disabled state. Userland gets `acctctl(int cmd, void *buf, size_t bufsz)`.

## Kernel State

Kernel builds define `ac_info_t`, which contains a lock, accounting output vnode, file name, enabled state, and resource bitmask. `struct exacct_globals` groups per-zone task, process, flow, and network accounting state and links it into a global list. `exacct_zone_key` is the zone key for per-zone settings.

## Research Notes

This header is relevant to filesystem behavior because accounting destinations are vnodes, and the kernel tracks whether accounting files are already in use across zones.
