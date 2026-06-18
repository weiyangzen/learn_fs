# File Research: sources/os/bsd/openbsd-src/sbin/mount/getmntopts.c

`getmntopts.c` implements shared parsing for comma-separated `-o` mount options. `getmntopts()` duplicates the option string and repeatedly calls `getmntopt()`; `getmntopt()` handles empty entries, `no` prefixes, `key=value` assignments, option-table lookup, flag setting/clearing, and integer/string option values.

Recognized options are defined by caller-provided `struct mntopt` tables. Options can set mount flags directly, return alternate flags for caller-specific handling, require values, accept optional values, or invert negative forms.

Unsupported options, missing/unexpected values, and illegal integer values are fatal via `errx()`. This parser is central to `mount` and most `mount_*` helpers.
