# File Research: sources/local-fs/xfsprogs/repair/progress.h

## Role

`progress.h` defines progress report IDs and declares the progress-reporting API.

## Interface

- Phase and report constants map repair phases to progress messages.
- `init_progress_rpt()`, `stop_progress_rpt()`, `set_progress_msg()`, `print_final_rpt()`, `timestamp()`, `duration()`, and `summary_report()` are exported.
- `PROG_RPT_INC(a,b)` increments progress only when AG striding and progress reporting are active.
- `do_parallel` is declared as a shared repair setting.

## Dependencies

Consumers rely on global `ag_stride`, `prog_rpt_done`, and phase-specific constants matching `progress.c`.

## Risk Areas

The report ID constants must stay in sync with the `progress_rpt_reports` array ordering in `progress.c`.
