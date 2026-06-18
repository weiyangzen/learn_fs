# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-list-simplestreams.sh

## Scope

List-output regression test for Simplestreams-backed virt-builder sources.

## Behavior

- Points `VIRT_BUILDER_DIRS` at the Simplestreams fixture.
- Checks exact short `--list` output for CirrOS powerpc, x86_64, and i386 templates.
- Checks exact `--list --long` output, including source URI, names, arches, sizes, and aliases.
- Checks exact JSON list output and schema version.

## Dependencies And Risks

- Highly sensitive to output formatting, ordering, size formatting, and Simplestreams selection rules.
- Uses local file URI fixture and disables cache/signature checks.
