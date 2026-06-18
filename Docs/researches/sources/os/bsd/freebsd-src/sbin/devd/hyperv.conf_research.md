# File Research: sources/os/bsd/freebsd-src/sbin/devd/hyperv.conf

## Purpose
Defines Hyper-V-specific device event behavior.

## Main Elements
- Starts/stops `hv_kvp_daemon` on `hv_kvp_dev` create/destroy.
- Starts/stops `hv_vss_daemon` on `hv_fsvss_dev` create/destroy.
- Handles non-transparent network VF workflow with `hyperv_vfup` and `hyperv_vfattach`.

## Dependencies And Integration
Installed when Hyper-V support is enabled. Integrates DEVFS events, Hyper-V VF events, and Ethernet attach events with Hyper-V helper scripts.
