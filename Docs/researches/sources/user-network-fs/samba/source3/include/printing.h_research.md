# sources/user-network-fs/samba/source3/include/printing.h

## Purpose
`printing.h` defines Samba's low-level print subsystem contracts below spoolss. It abstracts platform print backends, print job state, queue status, print database handles, spool file handling, print notification registration, and print queue/job operations.

## Important APIs, Types, And Control Flow
Queue/job states include LPQ statuses and Samba's `PJOB_SMBD_SPOOLING`. `print_queue_struct` holds system job metadata, `print_status_struct` describes queue state, and `struct printjob` tracks smbd-launched spool jobs with pid, spoolss job id, system job id, fd, status, size, names, user/client, queue, and devmode. `struct printif` is the backend vtable for queue fetch/pause/resume, job delete/pause/resume/submit. The file declares generic, CUPS, and iPrint backends, job id mapping helpers, spool open/write/end/terminate paths, print job lifecycle functions, queue pause/resume/purge/status functions, backend initialization, LPQ parsing, print TDB open/release/close helpers, notify pid list access, and message receive handling.

## State And Persistence
Persistent state includes print TDBs (`PRINT_DATABASE_VERSION`), job id mappings, notify pid lists under `NOTIFY_PID_LIST_KEY`, spool files named with `PRINT_SPOOL_PREFIX`, backend system queue jobs, and printer-specific TDB handles with refcounts. Transient state lives in `printjob` records and queue/status structs.

## Dependencies And Integration Points
It depends on TDB, loadparm printing types, messaging, tevent, auth session info, spoolss devmode, files/connections, and CUPS/iPrint optional backends. It integrates with smbd file spooling, spoolss RPC, Unix print systems, printcap discovery, notification messaging, and platform-specific print commands.

## Risks And Test Signals
Risks include job id wraparound, stale print database handles, mismatched system job and spoolss job ids, backend command parsing differences, notify pid cleanup failures, spool file leaks, and platform default selection errors. Test signals include CUPS/BSD/SYSV backend queue parsing, job start/write/end/delete/pause/resume, queue pause/resume/purge, TDB version handling, print notify registration cleanup, system job id mapping, spool termination on close/error, and build tests with and without CUPS/iPrint.
