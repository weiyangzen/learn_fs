# File Research: sources/virtualization/guestfs-tools/drivers/test-virt-drivers-linux.sh

## Scope

Runtime output regression test for `virt-drivers` on the phony Fedora guest.

## Behavior

- Requires the Fedora phony guest.
- Runs `virt-drivers --format=raw -a fedora.img` into `actual-fedora.xml`.
- Diffs against `expected-fedora.xml`, ignoring generated-by lines.
- Removes actual output afterward.

## Dependencies And Risks

- Exact XML structure is asserted aside from generated version comment.
