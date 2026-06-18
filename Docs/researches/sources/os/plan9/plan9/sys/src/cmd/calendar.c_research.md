# File Research: sources/os/plan9/plan9/sys/src/cmd/calendar.c

Plan 9 `calendar` reminder matcher. It builds a linked list of regular expressions for today, tomorrow, weekend carry-over days, and optionally a user-specified ahead day.

Options are `-y` to require matching year, `-d` to print generated regexps, and `-p days` to add a future day. With no files it reads `/usr/$user/lib/calendar`; otherwise it scans provided files.

`dates` emits regexps for month-day, day-month, `every <weekday>`, and `the <nth> <weekday>`. Input lines are lowercased before matching; matching original lines are printed.
