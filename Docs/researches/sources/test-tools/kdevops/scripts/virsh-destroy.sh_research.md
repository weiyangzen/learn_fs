# sources/test-tools/kdevops/scripts/virsh-destroy.sh

## Purpose
Destroys all currently listed libvirt domains whose names contain `kdevops`.

## Important APIs and control flow
The script loops over `virsh list | awk '{print $2'} | grep kdevops`, echoes each matched domain name, and runs `virsh destroy` on it.

## State and dependencies
Mutates libvirt domain runtime state by forcibly stopping every matching running VM. Depends on `virsh` and the caller's libvirt permissions/session.

## Integration points
Can be called by Make or cleanup targets to stop all active kdevops guests in the current libvirt session.

## Risks and test signals
Destroy is abrupt and can lose guest state. Matching is based only on domain name substring and ignores stopped domains because `virsh list` omits inactive guests. Test in a session containing only disposable kdevops domains.
