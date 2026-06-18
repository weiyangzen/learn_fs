# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/q/runq.c

## Purpose
Queue runner for retrying and completing upas queued deliveries.

## Main Interfaces
- `main`: option parsing and queue root selection.
- `doalldirs`, `dodir`, `rundir`: scan user queue directories.
- `dofile`: process one `C.*`/`D.*` queue item.
- `returnmail`: bounce failed mail back to sender.
- `doload`: global load-file limiter.

## Behavior
`runq` scans `C.*` control files, verifies matching data files, respects retry backoff based on `E.*` error-file age, locks control files, keeps locks alive with a helper process, executes the configured delivery command with the data file on stdin and errors appended to `E.*`, and removes all matching queue files on success or permanent failure. Temporary bad systems are skipped for the rest of a run.

## Dependencies
Queue naming conventions, `Mlock`, `sysopenlocked`, `upas/marshal` for bounces, `returnable`, syslog.

## Risks / Notes
- Give-up default is 2 days unless `-R` disables permanent give-up.
- Control-file argument parsing is whitespace/quote aware but simple.
- Bounce suppression avoids postmaster and unreturnable senders.
