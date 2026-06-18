# sources/test-tools/strace/src/scsi.c

Purpose: top-level SCSI ioctl decoder, routing SG_IO v3/v4 requests and decoding common SCSI generic ioctls.

Important APIs/types/functions: `decode_sg_io`, `decode_sg_scsi_id`, `scsi_ioctl`, `decode_sg_io_v3`, `decode_sg_io_v4`, `decode_sg_req_info`, and xlat tables for SG commands/reset flags.

Control flow: for `SG_IO`, entry reads the first 32-bit interface id from the user struct: `'S'` dispatches to v3 and `'Q'` to v4; other ids are printed indirectly. On exit it retrieves the saved interface id from tcb private data and completes response decoding. Other cases decode `SG_GET_SCSI_ID`, request tables, reset flags, pointer integers, value arguments, or return pointer integers only on exit.

State and persistence behavior: uses tcb private data indirectly via the v3/v4 decoders to remember the interface id and entry-side transfer metadata. No durable state beyond syscall entry/exit.

Dependencies and integration points: compiled with richer support when `<scsi/sg.h>` is available. Integrates with the generic ioctl dispatcher and SCSI generic request info decoder.

Risks: SG ioctls mix in/out pointers and interface-id versioning; failure to save entry data leads to unbalanced struct printing. Header availability changes coverage, so build configurations need both paths.

Test signals: exercise SG_IO v3 and v4, unknown interface ids, SG reset bit combinations, pointer integer set/get commands, `SG_GET_SCSI_ID`, and exit-only decode behavior.
