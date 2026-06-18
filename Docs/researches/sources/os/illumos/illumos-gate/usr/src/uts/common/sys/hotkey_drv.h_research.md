# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotkey_drv.h

## Role

`hotkey_drv.h` defines shared structures and prototypes for the ACPI hotkey driver and vendor-specific hotkey support.

## Key Interfaces and Data

- `ID_LEN` is 9 for ACPI hardware/unique ID strings.
- `struct acpi_drv_dev` stores ACPI handle, HID, UID, address, validity, present state, device type, index, and minor.
- `hotkey_drv_t` is driver soft state: embedded ACPI device, devinfo pointer, vendor-private data, lock pointer, selected hotkey method, module ID, vendor ioctl/fini callbacks, ACPI video flag, and ACPI video state.
- `struct vendor_hotkey_drv` records vendor ID, module name, and enable flag.
- Status/debug constants include `HOTKEY_DRV_OK`, `HOTKEY_DRV_ERR`, `HOTKEY_DBG_NOTICE`, and `HOTKEY_DBG_WARN`.
- Method flags distinguish none, vendor, ACPI video, and combined miscellaneous support.
- Externs include global `acpi_hotkey` and `hotkey_drv_debug`.
- Declares ACPI helpers for setting integer methods, generating sysevents, initializing ACPI device metadata, hotkey init/fini, hotkey ioctl, ACPI video ioctl, brightness inc/dec, and hotkey sysevent generation.

## Dependencies and Use

The header includes kernel DDI/module, ACPI, sysevent, and `acpi_drv` dependencies. It is internal to ACPI hotkey implementation files and vendor modules.

## Research Notes

The design allows a generic hotkey core to delegate vendor-specific behavior through dynamically loaded module callbacks while optionally integrating ACPI video brightness handling.
