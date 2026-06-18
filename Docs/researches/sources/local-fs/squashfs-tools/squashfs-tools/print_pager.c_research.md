# File Research: sources/local-fs/squashfs-tools/squashfs-tools/print_pager.c

Pager and wrapping support for help output. It parses `PAGER` safely into argv without invoking a shell, handling simple quotes and backslash behavior while rejecting common shell metacharacters such as pipes, separators, redirects, and background operators unless quoted/backslashed as data.

`launch_pager()` chooses stdout when paging is disabled or stdout is not a terminal; otherwise it forks a pager process. Pager detection runs `--version` to distinguish `less`, `more`/`pager`, and unknown pagers, adding friendly one-screen options where supported. Fallback chain is pager, less, more, cat, then in-process `simple_cat()`.

`get_column_width()` honors `user_cols`, terminal width, or defaults to 80. `autowrap_print()` and `autowrap_printf()` wrap text at word boundaries while preserving tab indentation.

Global controls: `no_pager` and `user_cols`.
