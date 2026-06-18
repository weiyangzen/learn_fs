# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_meter.c

Implements once-per-second VM paging and free-memory metering used by the swapper and pageout policy.

Key responsibilities:
- Updates 5-second and 30-second exponentially smoothed free-memory averages (`avefree`, `avefree30`).
- Aggregates per-CPU page-in and page-out counters and updates 5-second `pginrate` and `pgoutrate`.
- Decays the global `deficit` estimate when pageout is active.

Important details:
- Uses the `ave()` macro for fixed-window smoothing.
- Computes global page activity from each CPU's `vm.pgin` and `vm.pgout` stats.
- Deficit decay assumes useful pages per paging I/O are roughly half of a `MAXBSIZE` transfer, with a minimum useful page count of one.
- Skips deficit decay when `lotsfree` is zero or pageout is disabled through `dopageout`.

Filesystem relevance:
- Indirect but important. Page-in/page-out rates and deficit behavior are driven by filesystem-backed and swap-backed paging I/O, and the comments note the assumptions are imperfect across filesystem types.
