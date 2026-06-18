# File Research: sources/os/bsd/openbsd-src/sbin/restore/main.c

## Purpose

Top-level option parsing and mode dispatch for the restore program.

## Global State

Defines restore-wide flags (`bflag`, `cvtflag`, `dflag`, `vflag`, `yflag`, `hflag`, `mflag`, `Nflag`), command mode, dump number, volume number, tape block count, inode maps, max inode, dump times, terminal pointer, and temp directory.

## Main Flow

`main()` sets a restrictive umask for temp files, chooses input tape from `$TAPE` or default, chooses temp directory from `$TMPDIR` or default, accepts obsolete non-dash option syntax through `obsolete()`, parses modern flags, requires exactly one command among interactive, resume, full/incremental restore, table/list, and extract modes, installs interrupt handlers, registers `cleanup()`, and calls `setinput()`.

Mode dispatch:

- `i`: setup, extract directories with modes, initialize a new symbol table, run interactive shell.
- `r`: setup; if incremental, load existing symbol table, extract dirs, remove old leaves, compute node updates, resolve links, remove old nodes; if level zero, initialize fresh state; then extract leaves, create links, set directory modes, check, optionally verify, and checkpoint symbol table.
- `R`: resume from existing symbol table, skip maps/dirs, continue leaf extraction, links, modes, checks, and checkpoint.
- `t`: setup, extract dirs without modes, initialize symbol table, list requested paths.
- `x`: setup, extract dirs with modes, initialize symbol table, mark requested paths, extract files, create links, set modes, optional check.

## Obsolete Syntax

`obsolete()` converts historical compact restore options and ordered arguments into `getopt()`-compatible argv. Options requiring arguments (`b`, `f`, `s`) consume following argv entries and are rewritten as `-xVALUE`; other flags are grouped behind a single dash.

## Risks And Invariants

- Command modes are mutually exclusive and one is required.
- `atexit(cleanup)` is registered before setup proceeds so temporary directory/mode files are removed.
- `Nflag` dry-run mode is global and honored by lower layers for writes/checkpoints.
- The mode switch assumes `setup()` populates maps, tape metadata, and `curfile` for all modes except resume.
