# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp_util.h

Defines FCP utility ioctl command values and user/kernel exchange structures. Commands cover target inquiry/create/delete, sending a SCSI command, state count, and target mapping retrieval.

`struct fcp_ioctl` carries an fp minor number plus a variable list pointer. `struct device_data` reports target WWN, status, LUN count, and LUN0 type. `struct fcp_scsi_cmd` describes a passthrough SCSI command including FC port number, target PWWN, FC/SCSI status, packet state/action/reason, LUN, read flag, timeout, CDB buffer, data buffer/residual/status, and request-sense buffer.

The file also defines T11 target mapping structures (`fc_hba_mapping_entry_t`, `fc_hba_target_mappings_t`) and 32-bit syscall variants/conversion macros for ioctl and SCSI command structures. Pointer-width conversion here is ABI-sensitive.
