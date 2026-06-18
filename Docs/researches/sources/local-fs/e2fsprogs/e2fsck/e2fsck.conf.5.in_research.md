# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.conf.5.in

## Purpose
Manual page template for `e2fsck.conf(5)`, the configuration file controlling default e2fsck behavior.

## Configuration Areas
Documents INI-style stanzas:
- `[options]`: cancellation, time-fudge/system-clock behavior, test flag clearing, battery deferral, indexed-directory slack, inode count fullmap, logging, problem squelching, extent optimization, readahead, reporting.
- `[defaults]`: undo directory behavior.
- `[problems]`: per-problem overrides for messages, preen behavior, maximum counts, default answers, forced no-fix behavior, and not-a-fix optimization markers.
- `[scratch_files]` when enabled: directory, thresholds, dirinfo/icount scratch-file usage.

## Logging Contract
Defines percent expansions used by `logfile.c`: date/time, hostname, device basename, PID, epoch seconds, username, UTC modifier, and year/month/day fields.

## Integration
Generated to `e2fsck.conf.5` by the makefile. Its settings map directly into profile reads in `dirinfo.c`, `logfile.c`, and other e2fsck option/config code.

## Risks / Notes
The `[problems]` section can change repair behavior and is explicitly documented as source-code-sensitive.
