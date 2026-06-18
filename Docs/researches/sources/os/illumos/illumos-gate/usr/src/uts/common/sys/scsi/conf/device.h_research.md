# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/device.h

This header defines `struct scsi_device`, the SCSA target/lun/sfunc device representation used by target drivers and HBA nexus code.

Key definitions:
- `struct scsi_device` contains:
  - `sd_address` routing information and transport pointer
  - `sd_dev` devinfo pointer
  - target driver mutex
  - HBA-private and target-private pointers
  - inquiry and request sense pointers
  - FMA capability state
  - optional MPxIO pathinfo pointer
  - flags preventing uninitialization or duplicate `tran_tgt_free`
  - `sd_tran_safe`, a compatibility hack for older non-SCSA direct-access drivers
- Declares public kernel interfaces `scsi_probe()` and `scsi_unprobe()`.
- Declares private property access/update/remove/free helpers for device/path properties.
- Declares `SCSI_HBA_ADDR_COMPLEX` helper interfaces: `scsi_address_device()`, `scsi_device_hba_private_set()`, and `scsi_device_hba_private_get()`.
- Declares obsolete `scsi_slave()` and `scsi_unslave()`.

Dependencies:
- Includes `sys/scsi/scsi_types.h`.
- Uses kernel types such as `dev_info_t`, `kmutex_t`, `scsi_address`, and `scsi_hba_tran`.

Impact:
- This is a central SCSA ABI/API structure for target drivers.
- It documents how device private data, HBA private data, inquiry data, and MPxIO path properties are associated with target device nodes.

Cautions:
- The structure has historical compatibility fields and warnings about older `SCSI_HBA_TRAN_CLONE` and direct-access drivers overwriting transport vectors.
- The optional `SCSI_SIZE_CLEAN_VERIFY` padding exists to detect driver dependencies on structure size.
