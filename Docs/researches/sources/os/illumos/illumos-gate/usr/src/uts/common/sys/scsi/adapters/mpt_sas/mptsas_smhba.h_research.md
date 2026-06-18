# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_smhba.h

## Purpose
Declares SM-HBA support interfaces and property names for the illumos `mpt_sas` driver. It is the header for exposing SAS HBA/PHY metadata, sysevents, and PHY kstats through the Solaris/illumos SM-HBA model.

## Main Interfaces
- SM-HBA property names:
  - `MPTSAS_NUM_PHYS`
  - `MPTSAS_NUM_PHYS_HBA`
  - `MPTSAS_SMHBA_SUPPORTED`
  - `MPTSAS_DRV_VERSION`
  - `MPTSAS_HWARE_VERSION`
  - `MPTSAS_FWARE_VERSION`
  - `MPTSAS_SUPPORTED_PROTOCOL`
  - `MPTSAS_VIRTUAL_PORT`
  - `MPTSAS_MANUFACTURER`
  - `MPTSAS_SERIAL_NUMBER`
  - `MPTSAS_MODEL_NAME`
  - `MPTSAS_VARIANT`
- Device-info helpers:
  - `IS_ATAPI_DEVICE(x)`
  - `IS_SATA_DEVICE(x)`
  - `DEVINFO_DIRECT_ATTACHED`
- SM-HBA functions:
  - `mptsas_smhba_setup()`
  - `mptsas_smhba_show_phy_info()`
  - `mptsas_smhba_set_all_phy_props()`
  - `mptsas_smhba_set_one_phy_props()`
  - `mptsas_smhba_log_sysevent()`
  - `mptsas_create_phy_stats()`
  - `mptsas_update_phy_stats()`
  - `mptsas_destroy_phy_stats()`
  - `mptsas_smhba_phy_init()`
  - `mptsas_smhba_phy_state_update()`

## Dependencies And Relationships
Includes `sys/nvpair.h` for `data_type_t` and `sys/scsi/adapters/mpt_sas/mptsas_var.h` for driver types such as `mptsas_t`, `mptsas_phymask_t`, and `smhba_info_t`. It complements the lower-level MPI SAS headers by publishing discovered PHY/device state as illumos device properties, sysevents, and kstats.

## Research Notes
The header is small but sits on an important observability boundary: it maps controller/SAS device data into OS-visible SM-HBA properties. The `IS_ATAPI_DEVICE` and `IS_SATA_DEVICE` masks align with SAS device-info flags, so callers must pass the same device-info bitfield used by MPI/SAS discovery code.
