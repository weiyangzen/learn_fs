# File Research: sources/os/plan9/9front/sys/src/cmd/calendar.c

Purpose: Plan 9 `calendar` command that scans calendar files for entries matching today, tomorrow, weekend extension days, or an optional future day.

Key points:
- Options: `-y` requires year matching, `-d` prints generated regexes, `-p days` adds a specific future day.
- Defaults to `/usr/$user/lib/calendar` when no files are supplied.
- Builds linked list of compiled regexes for date patterns.
- `dates` generates patterns for month-day, day-month, `every <weekday>`, and ordinal weekday forms like `the first monday`.
- Input lines are lowercased before regex matching, while original lines are printed.
- `emalloc` wraps allocation with fatal error handling.

Dependencies and interactions:
- Uses Plan 9 `<regexp.h>` and `<bio.h>`.
- Uses `getuser`, `time`, `localtime`, `open`, and `Brdline`.

Research notes:
- Matching is regex-based and intentionally supports abbreviated month/day names with optional suffixes.
- Weekend logic includes extra days when tomorrow lands on Saturday or Sunday.
