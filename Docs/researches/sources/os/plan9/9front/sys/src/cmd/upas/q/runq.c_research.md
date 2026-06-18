# File Research: sources/os/plan9/9front/sys/src/cmd/upas/q/runq.c

Runs queued mail jobs from upas queue directories.

Key responsibilities:
- Scans one user queue or all queue subdirectories.
- Locks a queue directory with `./rundir`.
- Finds `C.*` control files, validates matching `D.*`, applies retry/give-up policy, and starts delivery subprocesses.
- Runs up to `-n` concurrent jobs.
- Keeps control-file locks alive while jobs run.
- Redirects queued data file to command stdin and appends stderr to `E.*`.
- Removes all matching queue files on success or permanent failure.
- Returns failed mail to sender unless retry is requested or return is disabled.

Important functions:
- `rundir()` scans a queue directory and manages live jobs.
- `dofile()` validates a queue entry, parses control args, checks retry windows, locks, forks, and execs the configured command.
- `donefile()` interprets child status and removes/retries/returns mail.
- `remmatch()` removes all queue files sharing the base suffix.
- `returnmail()` invokes upas marshal with the original data file as an attachment.
- `file()` maps `C.*` names to `D.*`/`E.*`.

Filesystem relevance:
- Queue state is entirely file-based: `C`, `D`, `E`, `F` prefix files in per-user dirs.
- Uses Plan 9 file locks and keeps them fresh with a child reading the fd.
- Cleans empty queue dirs and logs queue operations.

Notable risks and quirks:
- Control-file parsing is whitespace-oriented with minimal quoted-string handling.
- `badsys` suppresses repeated attempts to the same system during one run.
- Give-up defaults to 2 days unless `-R`.
