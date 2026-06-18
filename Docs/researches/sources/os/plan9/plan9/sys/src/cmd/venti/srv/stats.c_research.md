# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/stats.c

Purpose: Defines Venti server statistic descriptors, counters, history collection, and binning.

Key behavior:
- `statdesc` maps `NStat` counter indices to display names.
- `statsinit` allocates a 90,000-sample ring and starts `statsproc`.
- `statsproc` snapshots global `stats` once per second.
- `setstat`, `addstat`, and `addstat2` update counters under `statslock`.
- `binstats` turns historical samples into min/max/avg bins over an absolute or relative time interval.

Dependencies:
- Uses `Stats`, `Statbin`, stat IDs from `dat.h`, Plan 9 locks, and `vtproc`.

Notable details:
- `statdesc` must remain synchronized with `dat.h:/NStat`.
- `printstats` is currently empty.
