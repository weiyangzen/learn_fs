<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/term-pager.go -->
# sources/object-store/minio-mc/cmd/term-pager.go

Purpose: implements a terminal pager writer backed by Bubble Tea viewport, with fallback to stdout if the TUI cannot initialize.

Important APIs/types/functions: `model`, its `Init`, `Update`, `View`, `headerView`, and `footerView`; `termPager`, `init`, `Write`, `WaitForExit`, and `newTermPager`.

Control flow: `termPager.Write` lazily initializes a Bubble Tea program in a goroutine. The pager waits for the first window-size render or an initialization error. Data written into `buf` is sent to the Bubble Tea model as strings, where content is accumulated and word-wrapped to viewport width. Key events `q`, `esc`, and `ctrl+c` quit. Footer renders scroll percentage and a simple progress bar.

State and persistence: all state is in memory: accumulated content, viewport dimensions, channels, and program status. No files are written.

Dependencies and integration points: depends on Bubble Tea, bubbles viewport, lipgloss, wordwrap, stdout fallback, and callers that need an `io.Writer`-like pager.

Risks and test signals: `Write` blocks on an unbuffered channel after initialization; callers must eventually allow the pager goroutine to receive. Tests should cover fallback path, window resize, quit handling, scroll percent rendering, and `WaitForExit` behavior before/after initialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/term-pager.go -->
