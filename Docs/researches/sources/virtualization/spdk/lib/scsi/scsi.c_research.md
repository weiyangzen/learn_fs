# File Research: sources/virtualization/spdk/lib/scsi/scsi.c

This file provides small common SCSI library functions: initialization/finalization stubs, trace registration, LUN ID format conversion, SBC opcode string lookup, and log component registration.

`spdk_scsi_init()` returns success and `spdk_scsi_fini()` is empty. Trace registration declares SCSI device and task owner/object types and registers `SCSI_TASK_DONE` and `SCSI_TASK_START` trace descriptions under the `scsi` trace group.

`spdk_scsi_lun_id_int_to_fmt()` converts integer LUN IDs into SCSI formatted LUN values. IDs below 256 use addressing method 0 and place the low 8 bits at bits 55:48. IDs below 16384 use method 1 and place 14 bits at bits 61:48. Larger IDs return zero. `spdk_scsi_lun_id_fmt_to_int()` reverses method 0 and method 1 encodings; unsupported methods return `0xffff`.

The SBC opcode table maps common block command opcodes to human-readable strings such as READ/WRITE variants, SYNCHRONIZE CACHE, UNMAP, VERIFY, WRITE SAME, FORMAT UNIT, and others. `spdk_scsi_sbc_opcode_string()` ignores the service action argument for now and returns `"UNKNOWN"` when the opcode is not in the table.

The file registers the `scsi` log component. Its main caveat is that variable-length CDB service-action lookup is explicitly not implemented.
