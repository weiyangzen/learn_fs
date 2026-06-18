# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_subr.c

## Role

Provides HSFS miscellaneous helpers: ISO/HSFS date conversion, filesystem warning throttling, directory validity checks, and HSFS read kstats setup/update.

## Main Behavior

- Defines `hsfs_error[]`, a per-error warning table used to emit nonfatal media consistency warnings once per mount unless marked repeatable.
- `hs_parse_dirdate()` parses short directory-entry timestamps into Unix `timeval`.
- `hs_parse_longdate()` parses long volume-descriptor timestamps and preserves hundredths of seconds as microseconds.
- `hs_date_to_gmtime()` converts 1970-2099 dates plus GMT offset into seconds since epoch, with leap-year handling.
- `hsfs_valid_dir()` validates that an HSFS directory record is nonempty and has directory type.
- `hs_log_bogus_disk_warning()` emits structured warnings for malformed ISO/Joliet/Rock Ridge data and sets per-mount error flags.

## Kstats

- Defines named kstats for mountpoint, pages lost, physical read pages, cache read pages, readahead pages, coalesced pages, and total requested pages.
- `hsfs_kstats_update()` snapshots counters while holding HSFS queue locks.
- `hsfs_setup_named_kstats()` creates and installs virtual named kstats.
- `hsfs_init_kstats()` and `hsfs_fini_kstats()` manage per-mount kstat lifetime.

## Dependencies And Interactions

- Used by HSFS node parsing and mount code for dates, warnings, and read statistics.
- References `hsfs_lostpage` from HSFS vnode/page code.
