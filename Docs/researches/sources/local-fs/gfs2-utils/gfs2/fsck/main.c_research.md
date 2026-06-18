# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/main.c

## Purpose
Defines the `fsck.gfs2` command-line frontend, global fsck state, pass sequencing, signal interruption behavior, final cleanup, and fsck-compatible exit status calculation.

## Main Elements
- Globals: lost+found inode/state, block progress counters, abort/skip flags, error counters, duplicate counters, `sb_fixed`, and logging level.
- `read_cmdline()`: parses `-a/-p`, `-f`, `-h`, `-n`, `-q`, `-v`, `-V`, and `-y`, enforcing mutually exclusive preen/yes/no modes.
- `interrupt()`: SIGINT handler offering abort, skip current pass, or continue.
- `check_statfs()`: recomputes total/free/dinode counts from resource groups and optionally rewrites the statfs file.
- `passes[]`: ordered pass table: `pass1`, `pass1b`, `pass2`, `pass3`, `pass4`, `check_statfs`.
- `fsck_pass()`: logs and times one pass, handles abort/skip state, exits on pass error.
- `startlog()` / `exitlog()`: syslog command and exit status.
- `main()`: initializes locale/syslog/options, calls `initialize()`, optionally exits early for clean preen, installs SIGINT handler, runs all passes, releases system inodes, fsyncs, destroys link maps and context, warns after superblock reset, and computes final status.

## Dependencies And Integration
Top-level integration point for `initialize.c`, pass modules, link maps, metawalk state, libgfs2 inode lifetimes, logging, syslog, and command-line policy.

## Behavioral Notes
Skipping pass1 is explicitly discouraged inside pass1 itself. Final status is `FSCK_OK` if no errors were found, `FSCK_NONDESTRUCT` if all found errors were corrected, and `FSCK_UNCORRECTED` otherwise.
