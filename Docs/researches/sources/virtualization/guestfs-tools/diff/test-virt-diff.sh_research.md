# File Research: sources/virtualization/guestfs-tools/diff/test-virt-diff.sh

## Scope

Runtime regression test for `virt-diff`.

## Behavior

- Requires phony Fedora guest.
- Creates a qcow2 overlay backed by the raw Fedora image.
- Modifies the overlay by touching `/diff` and appending text to `/etc/motd`.
- Runs `virt-diff` between the raw base and qcow2 overlay.
- Compares exact expected output, including added file row, changed file row, unified diff hunk, and end marker.
- Removes generated qcow2 file.

## Dependencies And Risks

- Depends on guestfish qcow2 overlay creation and exact phony guest `/etc/motd` contents.
- Exact output comparison covers both metadata row formatting and external diff output.
