# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/455

Purpose: golden fixture for UBSAN shift-out-of-bounds parsing in SUNRPC transport timeout calculation. Expected title is `UBSAN: undefined-behaviour in xprt_calc_majortimeo` and type is `UBSAN`.

Important APIs, types, and functions: parser coverage includes `__ubsan_handle_shift_out_of_bounds` filtering and stack title extraction. Kernel frames include `xprt_calc_majortimeo`, `xprt_do_reserve`, `xprt_reserve`, `call_reserve`, `__rpc_execute`, `rpc_execute`, `rpc_run_task`, `rpc_call_sync`, and `rpc_create_xprt`.

Control flow: the report identifies undefined behaviour at `net/sunrpc/xprt.c:597:14`, then shows the RPC client task path that reserves transport resources. The reporter must title from `xprt_calc_majortimeo` rather than the UBSAN helper.

State and persistence behavior: static sanitizer fixture with no panicked/corrupted state. It persists a deeper call chain through RPC task execution for parser regression coverage.

Dependencies and integration points: depends on UBSAN shift report detection, generic helper-frame suppression, and SUNRPC stack frame normalization. Integrates network filesystem/RPC behavior into the report suite.

Risks: many `rpc_*` frames are plausible but less precise than the timeout calculation function. Parser changes that over-trim `.cold` UBSAN helper paths should still preserve the next frame.

Test signals: `UBSAN: Undefined behaviour in net/sunrpc/xprt.c:597:14`, `__ubsan_handle_shift_out_of_bounds`, `xprt_calc_majortimeo+0x210/0x280`, and RPC reserve/execute frames.
