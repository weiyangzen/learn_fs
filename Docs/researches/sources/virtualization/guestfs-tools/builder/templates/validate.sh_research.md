# File Research: sources/virtualization/guestfs-tools/builder/templates/validate.sh

## Scope

Validation test for virt-builder template indexes.

## Behavior

- Forces `LANG=C` and exits on errors.
- Creates an empty temporary file.
- Runs `virt-index-validate index`.
- If `index.asc` exists, validates it too.
- Validates the empty temporary file, then removes it.

## Dependencies And Risks

- Requires the `virt-index-validate` binary.
- Empty-file validation confirms parser acceptance of empty indexes.
- Does not verify that `index.asc` cryptographically matches `index`.
