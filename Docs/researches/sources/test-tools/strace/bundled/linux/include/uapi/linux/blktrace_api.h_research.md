<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/blktrace_api.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/blktrace_api.h

Purpose: Linux blktrace UAPI definitions for block I/O trace categories, actions, record formats, and setup structures.

Important APIs/types: enums `blktrace_cat`, `blktrace_act`, and `blktrace_notify`; macros combining actions with category masks via `BLK_TC_ACT`; trace magic/version constants; structs `blk_io_trace`, `blk_io_trace2`, `blk_io_trace_remap`, `blk_user_trace_setup`, and `blk_user_trace_setup2`; setup state enum values.

Control flow: macro composition encodes action and category into integer/64-bit action fields. Version 2 widens action and name/mask fields.

State and persistence: ABI definitions for kernel tracing buffers and setup ioctls; real use creates kernel trace state.

Dependencies and integration: includes `<linux/types.h>` and supports strace decoding of blktrace ioctls and binary trace structures.

Risks: mixed 32-bit and 64-bit masks (`1 <<` versus `1ull <<`) require decoder width care. v1/v2 structure differences can cause mis-decoding if keyed on wrong ioctl/version. Test signals: decode `BLKTRACESETUP`/v2 setup and sample trace records with high category bits like zone or write-zeroes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/blktrace_api.h -->
