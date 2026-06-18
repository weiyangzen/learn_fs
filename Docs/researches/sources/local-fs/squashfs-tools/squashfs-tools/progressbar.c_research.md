# File Research: sources/local-fs/squashfs-tools/squashfs-tools/progressbar.c

Implements asynchronous progress display. A background thread wakes every 250 ms, updates spinner state, and redraws either a full progress bar or percentage-only mode.

Progress accounting tracks `cur_uncompressed` and `estimated_uncompressed`; metadata progress adds an estimated extra amount and advances via floating increment. `progress_bar_size()`, `inc_progress_bar()`, `dec_progress_bar()`, and metadata helpers update counters.

Terminal width is initialized and updated on `SIGWINCH`. Output is mutex-protected so errors/info can first force a newline, avoiding progress-bar corruption. Non-tty output is throttled to avoid massive logs.

Public controls enable/disable temporary display, set display state, switch to percentage mode, finish with a final 100% line, and route error/info printing through progress-safe functions.
