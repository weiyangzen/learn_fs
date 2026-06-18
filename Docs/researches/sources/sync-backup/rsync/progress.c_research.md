# sources/sync-backup/rsync/progress.c

Purpose: Implements rsync transfer progress display for per-file and aggregate progress modes.

Important APIs, types, and functions: Exports `want_progress_now`, `progress_init()`, `set_current_file_index()`, `instant_progress()`, `end_progress()`, and `show_progress()`. Internal `struct progress_history`, `msdiff()`, and `rprint_progress()` maintain recent throughput samples and format output.

Control flow: `progress_init()` seeds start time for non-server clients. `show_progress()` samples current time, optionally converts per-file offsets to aggregate offsets for `--info=progress2`, initializes or rotates a five-second history ring, suppresses output when stdout is not in the foreground process group, and calls `rprint_progress()`. `end_progress()` prints final progress, newline, and resets per-file state. `instant_progress()` emits a filename when needed before ending progress.

State and persistence behavior: Static state tracks start sample, rolling history, ring indexes, and current file index. It updates global `output_needs_newline` and reads global `stats`, `cur_flist`, and verbosity flags. State is process-local and resets at file boundaries.

Dependencies and integration points: Depends on `rsync.h`, `inums.h`, terminal process group APIs when available, logging via `rprintf()`, and file-list lookups via `flist_find()`.

Risks and test signals: Risks include division by zero, incorrect aggregate index math with incremental recursion, terminal carriage-return padding regressions, and foreground detection differences. Tests should validate `--progress`, `--info=progress2`, quiet mode, incremental recursion, and terminal/non-terminal output.
