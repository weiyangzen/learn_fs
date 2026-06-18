# File Research: sources/virtualization/guestfs-tools/drivers/hwdata_config.ml.in

## Scope

Configure-generated OCaml configuration for virt-drivers hwdata paths.

## Behavior

- Defines `dir` from substituted `@HWDATA_PKGDATADIR@`.
- Converts empty directory string to `None`, otherwise `Some dir`.
- Defines optional `pci_ids` and `usb_ids` paths by appending `pci.ids` and `usb.ids`.

## Dependencies And Risks

- Depends on `Std_utils.(//)` path join helper.
- If hwdata directory is absent, driver output omits vendor/device names.
