# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/454

Purpose: golden fixture for UBSAN out-of-bounds parsing in the V4L2 test pattern generator. Expected title is `UBSAN: undefined-behaviour in precalculate_color` and type is `UBSAN`.

Important APIs, types, and functions: parser-facing behavior is UBSAN recognition and guilty-frame selection. Kernel frames include `precalculate_color`, `tpg_recalc`, `tpg_calc_text_basep`, `vivid_fillbuff`, `vivid_thread_vid_cap_tick`, `vivid_thread_vid_cap`, `kthread`, and `ret_from_fork`.

Control flow: a Vivid video capture kernel thread hits a UBSAN out-of-bounds report at `drivers/media/common/v4l2-tpg/v4l2-tpg-core.c:942:56`. The reporter must skip UBSAN helper frames and title the report from `precalculate_color`.

State and persistence behavior: static fixture; the persisted state includes one expected title/type and a thread-driven call trace. No panic or corruption state is expected.

Dependencies and integration points: depends on UBSAN parsing and stack frame normalization. Integrates media/v4l2-tpg and vivid virtual video capture threads into Linux parser tests.

Risks: since the crash happens in a kernel thread rather than a syscall, parser logic should not depend on user RIP frames. Helper frame filtering must expose the media-specific function.

Test signals: UBSAN line for `v4l2-tpg-core.c:942:56`, `precalculate_color+0x304e/0x3830`, `vivid_fillbuff`, and `vivid_thread_vid_cap`.
