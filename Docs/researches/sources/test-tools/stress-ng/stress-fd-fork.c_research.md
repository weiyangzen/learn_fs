# sources/test-tools/stress-ng/stress-fd-fork.c

Purpose: implements `fd-fork`, which opens a large number of duplicate descriptors, repeatedly forks children, and stresses descriptor closing by normal `close()` loops or `close_range()`.

Important APIs/types/functions: `stress_fd_close_info_t` holds close metrics, close-range state, and min/max fd values. `stress_fd_files[]` maps `--fd-fork-file` choices to `/dev/null`, `/dev/random`, stdin, stdout, and `/dev/zero`. `stress_fd_close()` first attempts `shim_close_range(fd_min, fd_max, 0)` and falls back to closing the tracked fd array, updating nanosecond-per-close metrics. `stress_fd_fork()` owns option handling, descriptor duplication, fork fan-out, cleanup, and metric reporting.

Control flow: the stressor clamps `--fd-fork-fds` to `stress_fs_file_limit_get()`, mmaps the fd array and shared close-info state, opens the selected source fd, and then synchronizes. In each loop it duplicates the source fd in batches of 10000 until the requested or system limit is reached, forks up to eight children, optionally has children close the inherited descriptors, waits for them, and repeats while allowed.

State and persistence behavior: no filesystem state is created beyond opening the selected device or stdio fd. The mapped fd table persists across the stressor lifetime and is closed in `tidy_fds`; the close metrics are stored in the mapped info block and emitted before unmapping.

Dependencies and integration points: uses stress-ng mmap helpers, file-limit helper, fork/wait helpers, bogo and metrics APIs, and `shim_close_range`. It is registered as `CLASS_FILESYSTEM | CLASS_OS`, has `VERIFY_ALWAYS`, and exposes `fd-fork-fds` and `fd-fork-file` options.

Risks: high fd counts can exhaust process or system fd tables, memory, or fork capacity; the code handles this by reducing the effective fd count and exiting when no children can be forked. `close_range()` metrics count the full min/max range, not only fds that were definitely open. Child close behavior is random, so close-path coverage varies run to run.

Test signals: run with low and high `--fd-fork-fds`, each `--fd-fork-file` mode, and systems with/without `close_range()`. Confirm metrics for close latency, peak descriptors open, and seconds to open all descriptors appear, and verify no descriptors remain open after cleanup.
