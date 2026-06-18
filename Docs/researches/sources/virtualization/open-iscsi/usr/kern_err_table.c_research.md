# File Research: sources/virtualization/open-iscsi/usr/kern_err_table.c

## Purpose
`kern_err_table.c` maps kernel iSCSI error codes from `iscsi_if.h` to human-readable strings.

## API
`kern_err_code_to_string(int err)` uses a switch over kernel constants such as `ISCSI_OK`, `ISCSI_ERR_DATASN`, `ISCSI_ERR_DATA_OFFSET`, `ISCSI_ERR_MAX_CMDSN`, `ISCSI_ERR_EXP_CMDSN`, `ISCSI_ERR_BAD_OPCODE`, digest errors, session/connection failures, SCSI error recovery reset, and NOP timeout. Unknown values return `"Invalid or unknown error code"`.

## Integration Notes
The table is for reporting kernel iSCSI failure causes in userspace logs or CLI output. It depends on the kernel-facing iSCSI interface header, not the higher-level userspace `iscsi_err.h`.

## Risk Notes
The mapping must be kept aligned with kernel `iscsi_if.h` constants. New kernel error codes will fall to the generic unknown string until added.
