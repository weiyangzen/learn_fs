# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acpi_drv.h

## Purpose

`acpi_drv.h` defines ioctl commands, data structures, kstat layouts, and minor-number helpers for the ACPI battery, AC adapter, lid, display, and hotkey driver.

## Main Interfaces

`enum acpi_drv_ioctl` covers battery bay, info/status, AC count, power status, battery warning get/set, lid status/update, brightness levels, and brightness setting.

`batt_bay_t` reports bay count and battery presence bitmap. `acpi_bif_t` mirrors ACPI battery information fields such as design capacity, last full capacity, voltage, warning/low thresholds, granularity, model, serial, type, and OEM info. `acpi_bst_t` reports battery state, rate, remaining capacity, and voltage. `acpi_drv_warn_t` stores warning thresholds.

## Kstats and Device Types

The header defines kstat names and `kstat_named` structures for power, warning, BIF, and BST data. `enum acpi_drv_type` distinguishes unknown, control-method battery, AC, lid, display, and hotkey devices. Kernel builds define minor encoding/decoding macros.

## Research Notes

Not filesystem-specific, but it is part of the platform driver ABI. It shows a common illumos pattern of matching ioctls, kstats, and encoded minors.
