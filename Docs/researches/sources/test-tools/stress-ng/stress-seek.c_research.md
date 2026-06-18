# sources/test-tools/stress-ng/stress-seek.c

Purpose: implements the `seek` stressor, which creates a temporary sparse file and repeatedly performs random `lseek`, read, write, optional hole-punch, and invalid seek operations. It stresses filesystem offset handling, sparse extent traversal, 32/64-bit seek paths, and error handling around unusual `whence` and offset values.

Important APIs/types/functions: `stress_seek`, `stress_shim_lseek`, `max_off_t`, `stress_fs_temp_dir_make_args`, `stress_fs_temp_filename_args`, `stress_fs_type_get`, `stress_setting_get`, `stress_metrics_set`, `lseek`, optional `lseek64`, `read`, `write`, `shim_fallocate`, `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, `SEEK_DATA`, `SEEK_HOLE`, and `FALLOC_FL_PUNCH_HOLE`.

Control flow: the stressor clamps `seek-size`, creates and immediately unlinks a temporary file, seeks near the requested end, writes one 512-byte block, then enters the synchronized run loop. Each iteration seeks to random offsets for a write and read, optionally verifies full read size, exercises end/current/data/hole seeks, optionally follows data/hole transitions, optionally punches an 8 KiB hole, and finally performs deliberately invalid seeks on a bad fd, invalid offsets, invalid `whence`, and out-of-range data/hole offsets.

State and persistence behavior: persistent state is limited to one unlinked temporary file descriptor whose blocks and holes change during the run; cleanup closes the descriptor and removes the temp directory. Static metric variables accumulate sampled seek latency and total seek count across the worker lifetime.

Dependencies and integration points: registered through `stress_seek_info` with `CLASS_IO | CLASS_OS`, optional verification, and `seek-size`/`seek-punch` options. It depends on stress-ng filesystem helpers, random generators, global option flags for minimize/maximize/verify, and platform feature macros for optional seek and fallocate behavior.

Risks and test signals: filesystem-specific behavior is intentionally variable, so `EINVAL`, unsupported data/hole seeking, and `EOPNOTSUPP` on punching are tolerated in selected paths. Real failures are unexpected read/write/seek errors, verify-mode short reads, leaked temp files, incorrect size clamping, or metrics that never observe successful seeks.
