# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_ioctl.h

## Purpose
Defines the illumos `mpt_sas` user/kernel ioctl ABI for adapter information, firmware update, adapter reset, raw MPI passthrough, event queues, PCI info, firmware diagnostics, register access, disk topology queries, and enclosure LED control.

## Main Interfaces
- Ioctl command numbers:
  - `MPTIOCTL_GET_ADAPTER_DATA`
  - `MPTIOCTL_UPDATE_FLASH`
  - `MPTIOCTL_RESET_ADAPTER`
  - `MPTIOCTL_PASS_THRU`
  - `MPTIOCTL_EVENT_QUERY`
  - `MPTIOCTL_EVENT_ENABLE`
  - `MPTIOCTL_EVENT_REPORT`
  - `MPTIOCTL_GET_PCI_INFO`
  - `MPTIOCTL_DIAG_ACTION`
  - `MPTIOCTL_REG_ACCESS`
  - `MPTIOCTL_GET_DISK_INFO`
  - `MPTIOCTL_LED_CONTROL`
- Adapter and PCI structures:
  - `mptsas_pci_bits_t`
  - `mptsas_adapter_data_t`
  - `mptsas_pci_info_t`
  - adapter type constants for SAS-2 and SAS-3.
- Firmware and passthrough:
  - `mptsas_update_flash_t`
  - `mptsas_pass_thru_t`
  - data-direction constants for none/read/write/both.
- Event queue:
  - `MPTSAS_EVENT_QUEUE_SIZE`
  - `MPTSAS_MAX_EVENT_DATA_LENGTH`
  - `mptsas_event_query_t`
  - `mptsas_event_enable_t`
  - `mptsas_event_entry_t`
  - `mptsas_event_report_t`
- Firmware diagnostics:
  - `mptsas_diag_action_t`
  - `mptsas_fw_diag_register_t`
  - `mptsas_fw_diag_unregister_t`
  - `mptsas_fw_diag_query_t`
  - `mptsas_fw_diag_release_t`
  - `mptsas_diag_read_buffer_t`
  - action constants for register, unregister, query, read buffer, and release; error/flag constants for UID, post/release, app-owned, valid buffer, firmware buffer access, reregister, and force release.
- Register/disk/LED:
  - `mptsas_reg_access_t` with IO and memory read/write command constants.
  - `mptsas_disk_info_t`, `mptsas_get_disk_info_t`, and kernel-only `mptsas_get_disk_info32_t`.
  - `mptsas_led_control_t` and constants for set/get plus identify/fail/OK-to-remove LEDs.

## Dependencies And Relationships
Includes `sys/types.h` and uses illumos fixed-width types plus `caddr32_t` under `_KERNEL` for 32-bit compatibility. The pass-through, flash, event, and diagnostic payloads bridge userland management tools to MPI firmware messages defined in the `mpi2_*` headers in this group.

## Research Notes
This file is an externally visible ABI and must remain alignment-conscious for 32-bit and 64-bit applications. It uses integer-encoded user pointers (`uint64_t`) in several structures, while `mptsas_get_disk_info_t` uses a typed pointer and provides an explicit 32-bit kernel compatibility form. That split is a key detail for copyin/copyout and model conversion.
