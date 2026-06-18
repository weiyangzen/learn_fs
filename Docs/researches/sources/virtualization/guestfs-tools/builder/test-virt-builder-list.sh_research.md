# File Research: sources/virtualization/guestfs-tools/builder/test-virt-builder-list.sh

## Scope

List-output regression test for native virt-builder index sources.

## Behavior

- Points `VIRT_BUILDER_DIRS` at `builder/test-config`.
- Checks exact short `--list` output for phony Debian, Fedora, Fedora qcow2 variants, Ubuntu, and Windows.
- Checks exact long output, including notes and multiline notes.
- Checks exact JSON output including `notes` objects and hidden flags.

## Dependencies And Risks

- Exact text comparison makes this a strict output-format contract.
- Relies on generated `test-index.conf` pointing at the local test index.
