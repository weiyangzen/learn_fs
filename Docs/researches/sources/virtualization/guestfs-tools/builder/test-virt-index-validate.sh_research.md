# File Research: sources/virtualization/guestfs-tools/builder/test-virt-index-validate.sh

## Scope

Regression test for `virt-index-validate`.

## Behavior

- Forces `LANG=C`.
- Expects two bad index fixtures to fail validation.
- Expects four good index fixtures to pass validation.

## Dependencies And Risks

- Validates parser/validator acceptance and rejection behavior through fixture files.
- Does not inspect exact error messages.
