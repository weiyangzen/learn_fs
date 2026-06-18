# sources/user-network-fs/samba/source3/printing/tests/vlp.c

## Purpose

`vlp.c` implements a virtual lp command for Samba printing tests. It emulates `lpq`, `lprm`, print submission, queue pause/resume, and job pause/resume using a simple TDB-backed queue, allowing print backend tests without a real system spooler.

## Important APIs, Types, and Functions

- `struct vlp_job` stores owner, job ID, job name, size, status, submit time, and deletion flag.
- `get_job_list()` and `set_job_list()` fetch/store `LPQ/<printer>` arrays.
- `next_jobnum()` locks `JOBNUM/<printer>` and allocates job IDs starting at `PRINT_FIRSTJOB`.
- `set_printer_status()` and `get_printer_status()` manage `STATUS/<printer>`.
- Command handlers implement `lpq`, `lprm`, `print`, `queuepause`, `queueresume`, `lppause`, and `lpresume`.
- `main()` parses `tdbfile=...` and dispatches commands.

## Control Flow

The program opens or creates the provided TDB file, chmods it to `0666`, and dispatches based on the subcommand. `print` builds a job owned by the effective user, assigns a job number, and appends it to `LPQ/<printer>`. `lpq` prints printer status followed by non-deleted jobs in a tab-separated format; the first queued job is reported as spooling. `lprm` marks matching jobs as deleted. Queue and job pause/resume mutate status records or job status fields.

## State and Persistence

All test state is stored in the TDB file passed by `tdbfile=...`. Queue entries are raw arrays of `struct vlp_job`, job counters are `JOBNUM/<printer>`, and printer status is `STATUS/<printer>`.

## Dependencies and Integration Points

It depends on Samba printing status constants, TDB helpers, passwd lookup, and filesystem mode changes. Samba test configurations can use it as `lpq command`, `print command`, `lprm command`, and pause/resume commands.

## Risks and Edge Cases

- Queue arrays are raw structs, so format is architecture/build dependent and suited only for tests.
- `get_job_list()` returns `data.dptr` directly and `num_jobs` from size division; corrupt sizes are not explicitly rejected.
- `lprm_command()` does not free `job_list`.
- The final unknown-command error prints `argv[1]` instead of `argv[2]`.

## Test Signals

This file is itself a test helper. Useful checks are command-level tests for append/list/delete, status transitions, queue pause/resume, job pause/resume, missing arguments, and interoperability with Samba’s parsing of lpq output.
