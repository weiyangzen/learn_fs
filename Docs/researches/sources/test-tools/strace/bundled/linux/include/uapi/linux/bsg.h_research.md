<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/bsg.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/bsg.h

Purpose: block SCSI generic UAPI definitions for `sg_io_v4`, BSG io_uring commands, and packed SCSI completion status helpers.

Important APIs/types: protocol/subprotocol constants for SCSI command, task management, and transport; queue flags; `struct sg_io_v4` with request/response pointers, data-in/data-out transfer pointers, status outputs, residuals, and generated tags; `struct bsg_uring_cmd`; inline extractors/builders for `res2` fields in io_uring completion (`device_status`, `driver_status`, `host_status`, `sense_len`, `resid_len`).

Control flow: inline functions use shifts/masks to pack and unpack a 64-bit completion status.

State and persistence: ABI definitions for SCSI command submission; real use can perform device I/O.

Dependencies and integration: includes `<linux/types.h>`; strace decodes SG_IO/BSG and io_uring command payloads from these layouts.

Risks: many fields are userspace pointers and must be decoded with directionality and iovec counts. Packed `res2` requires correct bit widths. Test signals: decode `sg_io_v4` with flat and iovec transfers, and validate `bsg_scsi_res2_build` round-trips with extractors.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/bsg.h -->
