# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-planner.sh

## Scope

Slow planner/regression test for virt-builder output format and size combinations.

## Behavior

- Requires slow-test mode and local Fedora compressed/qcow2 artifacts.
- Iterates four Fedora template variants, four size choices, and three output format choices.
- Runs `virt-builder` for every combination with no cache and no signature check.
- Writes to a common `planner-output` file and removes it at the end.

## Dependencies And Risks

- Requires generated `fedora.xz`, `fedora.qcow2`, and `fedora.qcow2.xz`.
- Test is broad smoke coverage; it does not inspect each output beyond command success.
