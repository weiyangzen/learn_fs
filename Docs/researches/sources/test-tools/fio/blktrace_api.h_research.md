# `sources/test-tools/fio/blktrace_api.h`

Purpose: Provides local copies of Linux blktrace constants and wire structs used by fio to parse binary trace files without depending on a specific kernel header version.

Important APIs and types: Defines trace category bits `BLK_TC_*`, `BLK_TC_SHIFT`, `BLK_TC_ACT()`, basic action enum values such as queue/merge/issue/complete/remap, notify enum values, combined action macros `BLK_TA_*` and `BLK_TN_*`, `BLK_IO_TRACE_MAGIC`, `BLK_IO_TRACE_VERSION`, `struct blk_io_trace`, `struct blk_io_trace_remap`, and `struct blk_user_trace_setup`.

Control flow and integration: `blktrace.c` reads `struct blk_io_trace` records from binary files, validates magic/version, checks action/category bits, endian-swaps fields, and skips PDU payloads based on `pdu_len`.

State and persistence: Defines binary layouts for persisted blktrace files and ioctl setup structures; it has no runtime state itself.

Dependencies: Includes `<asm/types.h>` for fixed-width kernel-style integer aliases.

Risks and test signals: Because this mirrors kernel ABI, drift from current kernel blktrace definitions could break parsing or setup compatibility. Tests should parse known-good traces from representative kernels and compare action decoding against `blkparse` output.
