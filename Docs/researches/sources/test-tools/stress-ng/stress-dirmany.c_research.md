# sources/test-tools/stress-ng/stress-dirmany.c

Purpose: implements `dirmany`, which stresses directory scalability by creating and removing many files with progressively longer names and optional allocated file sizes.

Important APIs/types/functions: `stress_dirmany_filename()` builds deterministic names from the temp directory, a run-length of `x`, and a 16-digit hex index. `stress_dirmany_create()` creates files until time budget, stop, name-length limit, or filesystem failure; it can fallocate requested bytes and validates creation with `stat()`. `stress_dirmany_remove()` unlinks the generated sequence. `stress_dirmany()` owns option handling and metrics.

Control flow: the stressor creates a temp directory, resolves `--dirmany-bytes` with maximize/minimize behavior, synchronizes start, and loops create/remove phases. Creation uses about 60% of remaining timeout so cleanup has time. After removal, the next index continues unless it grows beyond one billion, where it wraps to avoid overflow.

State and persistence behavior: filesystem state is temporary files under a stress-ng temp directory, removed after every cycle and at final temp-dir removal. Runtime state tracks `i_start`, total created, max valid filename length, and timing accumulators. No durable state is kept.

Dependencies and integration points: depends on stress-ng temp helpers, `core-builtin`, fallocate shims, metrics, timeout globals, and `dirmany-bytes` option. Registered as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: filename-length probing treats `ENAMETOOLONG` by backing off; other open failures end the create phase. Large `dirmany-bytes` can consume disk space quickly despite timed removal. `stat()` failures other than `ENOMEM` are verification failures.

Test signals: run with default zero-byte files, small nonzero `--dirmany-bytes`, and maximize/minimize modes; inspect metrics for create/remove percentage and rates, and confirm no leftover temp files after interruption.
