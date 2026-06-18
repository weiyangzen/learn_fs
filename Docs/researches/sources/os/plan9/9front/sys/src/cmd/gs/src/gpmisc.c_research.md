# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.c

Purpose: Shared platform utility implementation for temp files and generic path normalization.

Temp helpers: `gp_gettmpdir` checks `TMPDIR` then `TEMP` using `gp_getenv`. `gp_fopentemp` converts stdio mode strings to `open` flags, uses `O_EXCL` with user read/write permissions, then wraps the descriptor with `fdopen`.

Path combining: `gp_file_name_combine_generic` concatenates prefix and filename, handles absolute filename roots, inserts platform separators, removes current-directory items, resolves parent-directory items when allowed, honors `no_sibling`, and returns small-buffer/cannot-handle statuses. It delegates platform-specific syntax decisions to functions such as `gp_file_name_root`, `gs_file_name_check_separator`, and `gp_file_name_is_parent`.

Other helpers: `gp_file_name_reduce` normalizes a single path by combining it with an empty suffix. `gp_file_name_is_absolute` checks for a nonzero root. `gp_file_name_parents` and `gp_file_name_cwds` compute leading parent/current-reference spans.

Dependencies and notes: This is deliberately shared across platforms; comments direct platform-specific changes into each platform’s `gp_file_name_combine` and syntax predicates.
