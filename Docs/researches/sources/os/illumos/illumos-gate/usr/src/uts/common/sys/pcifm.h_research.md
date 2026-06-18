# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcifm.h

## Purpose
Defines PCI/PCI-X fault-management data structures used to gather, preserve, and post PCI error-register state for ereports.

## Main Interfaces
- Device flags: `PCI_BRIDGE_DEV`, `PCIX_DEV`.
- Valid-bit masks for PCI status, bridge status/control, PCI-X status, ECC status, and PCI-X bridge status.
- Error register structures:
  - `pci_bdg_error_regs_t`
  - `pci_error_regs_t`
  - `pci_erpt_t`
  - `pcix_ecc_regs_t`
  - `pcix_error_regs_t`
  - `pcix_bdg_error_regs_t`
- Bus-specific and target-error structures:
  - `pci_fme_bus_specific_t`
  - `pci_target_err_t`
- `PCI_FM_SEV_INC(x)`: macro that increments severity counters based on `DDI_FM_*` status.

## Dependencies And Relationships
Includes `sys/dditypes.h` for `ddi_acc_handle_t` and uses `dev_info_t` plus DDI fault-management severity constants. It is consumed by PCI error-report setup/post/teardown paths.

## Research Notes
The structures are containers for snapshots of config-space and PCI-X ECC state. Valid flags are important because not every device or bridge exposes every register.
