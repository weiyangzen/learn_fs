# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/453

Purpose: golden fixture for UBSAN out-of-bounds parsing in LKDTM. Expected title is `UBSAN: undefined-behaviour in lkdtm_ARRAY_BOUNDS` and type is `UBSAN`.

Important APIs, types, and functions: parser coverage includes UBSAN report recognition and stack-based title extraction. Kernel frames include `__ubsan_handle_out_of_bounds`, `lkdtm_ARRAY_BOUNDS`, `lkdtm_do_action`, `direct_entry`, `full_proxy_write`, `__vfs_write`, `vfs_write`, and `ksys_write`.

Control flow: the report begins with a UBSAN undefined-behaviour line referencing `drivers/misc/lkdtm/bugs.c:243:16`, then a call trace from UBSAN epilogue through LKDTM's direct debugfs/proc entry and the write syscall. The parser should report the LKDTM action function rather than the generic UBSAN handler.

State and persistence behavior: static sanitizer fixture with no panic flag. It persists source-location details and module-qualified `[lkdtm]` frame names.

Dependencies and integration points: depends on Linux UBSAN oops patterns, module suffix handling, and frame filtering for sanitizer helpers. It integrates LKDTM fault injection into report tests.

Risks: title extraction could stop at `__ubsan_handle_out_of_bounds` or include `.cold`/module suffixes if normalization regresses.

Test signals: `UBSAN: Undefined behaviour in drivers/misc/lkdtm/bugs.c:243:16`, `__ubsan_handle_out_of_bounds.cold`, `lkdtm_ARRAY_BOUNDS.cold.2 [lkdtm]`, and write syscall frames.
