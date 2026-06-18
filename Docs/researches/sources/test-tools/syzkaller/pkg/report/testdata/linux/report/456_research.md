# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/456

Purpose: golden fixture for UBSAN shift-out-of-bounds parsing in F2FS mount setup. Expected title is `UBSAN: undefined-behaviour in f2fs_fill_super` and type is `UBSAN`.

Important APIs, types, and functions: parser behavior includes UBSAN source-line recognition and stack guilty-frame extraction. Kernel frames include `f2fs_fill_super.cold`, `mount_bdev`, `f2fs_mount`, `legacy_get_tree`, `vfs_get_tree`, `do_mount`, `ksys_mount`, and `__x64_sys_mount`.

Control flow: a mount syscall triggers undefined behavior at `fs/f2fs/super.c:2563:16`. The parser follows the UBSAN report into the filesystem superblock fill path and ignores unrelated perf-rate chatter interleaved later in the log.

State and persistence behavior: static non-panicking fixture. Persisted state is the expected UBSAN title/type and raw mount-path stack.

Dependencies and integration points: depends on UBSAN parsing, syscall stack handling, and filesystem frame normalization that drops `.cold` suffixes from the title. Integrates F2FS mount handling into report tests.

Risks: interleaved performance messages can disrupt contiguous report extraction. Title normalization should not emit `f2fs_fill_super.cold.79`.

Test signals: `UBSAN: Undefined behaviour in fs/f2fs/super.c:2563:16`, `__ubsan_handle_shift_out_of_bounds`, `f2fs_fill_super.cold.79`, and mount syscall frames.
