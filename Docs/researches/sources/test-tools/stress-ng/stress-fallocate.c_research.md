# sources/test-tools/stress-ng/stress-fallocate.c

Purpose: implements `fallocate`, a filesystem stressor that allocates, truncates, punches, zeroes, collapses, inserts, and invalidly fallocates ranges in temporary files.

Important APIs/types/functions: option `fallocate-bytes` controls total allocation size divided by worker instances. `modes[]` contains supported `fallocate()` flags; `illegal_modes[]` contains invalid flag combinations. `stress_fallocate()` drives temp-file setup, async/sync fds, mode permutation generation, allocation/truncation loops, optional size verification, and cleanup.

Control flow: the stressor computes per-instance size, reports expected disk usage, creates a temp directory and file, optionally opens a second `O_SYNC` fd, probes pathconf values, unlinks the name, and sync-starts. Each iteration uses `posix_fallocate()` or `fallocate()`, fsyncs, verifies file size when requested, truncates to zero and back, randomly applies supported modes at page-aligned offsets, walks all flag permutations, probes bad fds, illegal modes, pipe fds, and negative offsets/lengths, then increments bogo operations.

State and persistence behavior: file data lives in an unlinked temp file and is removed when descriptors close. The temp directory is removed at teardown. Runtime state includes mode permutations, ftruncate error counts, pipe fds, and filesystem type strings used in diagnostics.

Dependencies and integration points: gated on `HAVE_FALLOCATE`; uses stress-ng temp-dir, filesystem usage, flag permutation, shim fallocate/fsync/stat/unlink, bad-fd, and verification helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS` with optional verification.

Risks: can consume significant disk space or trigger filesystem-specific fallocate semantics. Some modes are Linux/filesystem dependent and may legitimately fail. Verification assumes successful allocation changes file size to the requested length for the chosen path, which may differ for keep-size or specialized modes only used after reset.

Test signals: run on tmpfs/ext4/xfs where available, with small and maximized `--fallocate-bytes`, with `--verify`, and confirm cleanup leaves no temp files while expected invalid operations do not produce failures.
