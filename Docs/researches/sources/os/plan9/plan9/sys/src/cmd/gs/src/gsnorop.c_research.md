# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnorop.c

Provides stubs for builds without implemented RasterOp support. `gs_current_logical_op` always returns `lop_default`; `gs_set_logical_op` accepts only `lop_default` and returns `rangecheck` for other logical operations.

Memory-device and default `copy_rop`/`strip_copy_rop` implementations return errors (`rangecheck` or `unknownerror`) to signal unsupported operations. ROP texture-device allocation also returns `rangecheck`, and the maker function is a never-called no-op.

This file satisfies link dependencies while intentionally disabling RasterOp behavior.
