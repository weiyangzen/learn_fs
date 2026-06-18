<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_sg_req_info.c -->
# sources/test-tools/strace/src/print_sg_req_info.c

Purpose: decodes `struct sg_req_info` for SCSI generic ioctl support.

Important APIs/types/functions: `decode_sg_req_info`, `struct_sg_req_info`, and `HAVE_SCSI_SG_H` gating.

Control flow: on entering returns without printing; on exit prints `argp` and decodes request state, orphan/ownership/problem flags, pack id, user pointer, and duration.

State and persistence behavior: no state.

Dependencies and integration points: used by SG ioctl decoder paths; depends on `<scsi/sg.h>` and mpers when available.

Risks: compiled only when SCSI SG headers are present. Output is exit-only because ioctl fills the structure.

Test signals: successful `SG_GET_REQUEST_TABLE`-style output, failed ioctl, invalid pointer, and builds without `<scsi/sg.h>`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_sg_req_info.c -->
