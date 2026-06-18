# sources/test-tools/kdevops/scripts/vfio-permissions.sh

## Purpose
Prepares host VFIO/PCI sysfs permissions for specified PCI device IDs used by passthrough workflows.

## Important APIs and control flow
The script is immediate-execution shell with `set -e`. It requires at least one PCI ID, loads `vfio-pci`, grants group `libvirt` access to `/sys/bus/pci/drivers_probe`, copies `10-qemu-hw-users.rules` into `/etc/udev/rules.d/` and `10-qemu-limits.conf` into `/etc/security/limits.d`, then for each PCI ID adjusts group/mode on `driver_override` and `driver/unbind`.

## State and dependencies
Mutates host kernel module state, sysfs node permissions, udev rules, and security limits. Requires `sudo`, `modprobe`, a `libvirt` group, and valid `/sys/bus/pci/devices/<PCI-ID>` paths.

## Integration points
Supports PCI passthrough and QEMU/libvirt workflows that need non-root libvirt users to bind/unbind devices to VFIO.

## Risks and test signals
Changing sysfs permissions is host-global and may be reset by udev or reboot. The script assumes a `libvirt` group and does not validate each PCI ID before chmod/chgrp. Test with a disposable passthrough device and verify libvirt/QEMU can unbind and bind it afterward.
