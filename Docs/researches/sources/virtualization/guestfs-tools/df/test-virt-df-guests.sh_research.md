# File Research: sources/virtualization/guestfs-tools/df/test-virt-df-guests.sh

## Scope

Libvirt-backed smoke test for `virt-df`.

## Behavior

- Uses the phony guest libvirt XML via `test://.../guests.xml`.
- Runs `virt-df -c "$libvirt_uri"`.

## Dependencies And Risks

- Requires libvirt test driver and generated phony guest XML.
- Does not assert exact output; command success is the check.
