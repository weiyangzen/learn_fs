# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnorop.c

Stubs for builds without implemented RasterOp support.

Key behavior:
- `gs_current_logical_op` always returns `lop_default`.
- `gs_set_logical_op` accepts only `lop_default`; all other values return `rangecheck`.
- Memory-device RasterOp entry points return `rangecheck`.
- Default device `copy_rop` and `strip_copy_rop` implementations return `unknownerror`.
- `gx_alloc_rop_texture_device` returns `rangecheck`.
- `gx_make_rop_texture_device` is an empty never-called stub.

Dependencies:
- Provides symbols expected by RasterOp-capable interfaces while intentionally disabling behavior.

Research notes:
- This file is a compatibility stub layer, useful for configurations that compile RasterOp APIs but do not support the feature.
