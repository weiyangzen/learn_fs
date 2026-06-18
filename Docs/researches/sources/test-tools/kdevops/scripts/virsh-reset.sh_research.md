# sources/test-tools/kdevops/scripts/virsh-reset.sh

## Purpose
Resets all currently listed libvirt domains whose names contain `kdevops`.

## Important APIs and control flow
The script loops over `virsh list | awk '{print $2'} | grep kdevops` and runs `virsh reset` on each matched running domain.

## State and dependencies
Mutates all matching running VMs by issuing hard resets. Depends on `virsh` and appropriate libvirt permissions.

## Integration points
Used by watchdog or manual recovery paths that need all active kdevops guests rebooted without graceful shutdown.

## Risks and test signals
Hard resets can corrupt guest state if storage is active. Matching is broad and only sees active domains. Test in an isolated libvirt session and confirm only intended `kdevops` domains reset.
