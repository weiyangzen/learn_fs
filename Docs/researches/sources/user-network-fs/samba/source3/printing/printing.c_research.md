# sources/user-network-fs/samba/source3/printing/printing.c

## Purpose

`printing.c` is the main Samba source3 print backend implementation. It owns per-printer job records, queue cache refresh, spool job start/end/delete/pause/resume operations, queue pause/resume/purge operations, and notification emission for spoolss consumers. It bridges SMB/SPOOLSS-visible jobs to backend-specific print interfaces selected from `printing =` service configuration.

## Important APIs, Types, and Functions

- `print_backend_init()` creates the cache directory, initializes or wipes per-printer TDBs when `PRINT_DATABASE_VERSION` changes, closes cached DB handles, and calls `nt_printing_init()`.
- `printing_end()` closes all cached print DBs.
- `get_printer_fns_from_type()` and `get_printer_fns()` select `generic_printif`, `cups_printif`, or `iprint_printif` and set the interface type.
- `print_key()` builds binary uint32 TDB keys for job records.
- `pack_devicemode()` and `unpack_devicemode()` serialize `spoolss_DeviceMode` with NDR and store it in a TDB-packed blob.
- `unpack_pjob()` and `pjob_store()` decode and encode `struct printjob` records.
- `print_job_find()`, `print_job_exists()`, `print_job_devmode()`, `print_job_set_name()`, and `print_job_get_name()` expose stored job lookup and metadata operations.
- `sysjob_to_jobid_pdb()`, `sysjob_to_jobid()`, and `jobid_to_sysjob_pdb()` map OS spooler job numbers to Samba job IDs by traversing print DB records.
- `print_queue_update_internal()`, `print_queue_update_with_lock()`, `print_queue_receive()`, and `print_queue_update()` refresh the internal queue cache from the backend lpq interface, either locally or through `samba-bgqd`.
- `print_queue_length()` and `print_queue_status()` provide cached queue status and queue snapshots.
- `print_job_start()`, `print_job_write()`, `print_job_endpage()`, and `print_job_end()` implement the lifecycle of an SMB print job.
- `print_job_delete()`, `print_job_pause()`, `print_job_resume()`, `print_queue_pause()`, `print_queue_resume()`, and `print_queue_purge()` implement administrative and owner-visible controls.
- `print_notify_register_pid()` and `print_notify_deregister_pid()` maintain per-printer notification subscriber PID/refcount lists.

## Control Flow

Startup calls `print_backend_init()`, which opens each printable service DB, locks `INFO/version`, wipes stale DB format versions, then initializes NT printing. Job creation enters `print_job_start()`: access, time, disk-space, autoloaded-printer, and max-job checks run first; `allocate_print_jobid()` locks `INFO/nextjob`, advances the cyclic job ID, stores an empty placeholder, and returns the chosen ID. The job is filled with PID, client, user, queue, devmode, spool state, and a spool file from `print_job_spool_file()`, then `pjob_store()` persists it and appends it to `INFO/jobs_added`.

Writes go through `print_job_write()` only for the creating process and only while not in `PJOB_SMBD_SPOOLING`. `print_job_end()` handles normal or shutdown close by sizing the file, rejecting zero-length or deleting jobs, running the backend `job_submit` callback, switching the job to spooled/queued, and forcing or requesting queue refresh when the cache is stale. Error close or submission failure unlinks the spool file and deletes the job record.

Queue refresh starts with `print_queue_length()` or `print_queue_status()` checking `print_cache_expired()`. If needed, `print_queue_update()` either sends a `MSG_PRINTER_UPDATE` to `samba-bgqd` or performs the update locally. The update path throttles duplicate requests with `MSG_PENDING/<share>`, serializes refreshes with `LOCK/<share>` and `UPDATING/<share>`, runs backend `queue_get`, sorts by submission time, updates or creates jobs, deletes stale records via `traverse_fn_delete()`, stores `INFO/linear_queue_array`, updates `INFO/total_jobs`, writes `STATUS/<share>`, and clears pending state.

Deletion and pause/resume first validate ownership or administrative access. `print_job_delete1()` marks jobs `LPQ_DELETING`, calls backend `job_delete` when already spooled, deletes successful records, and updates the rough job count. `print_job_delete()` also handles unspooled spool-file removal for the owning process, forces a refresh, and returns `WERR_PRINTER_HAS_JOBS_QUEUED` when the job is still deleting.

## State and Persistence

The durable state is in per-printer cache TDBs under `cache_path("printing/")`. Important records include binary job-id keys containing packed `struct printjob`, `INFO/version`, `INFO/nextjob`, `INFO/total_jobs`, `INFO/jobs_added`, `INFO/jobs_changed`, `INFO/linear_queue_array`, `STATUS/<share>`, `CACHE/<share>`, `MSG_PENDING/<share>`, `UPDATING/<share>`, and notification PID lists. Spool data is stored in files under the printer path using `PRINT_SPOOL_PREFIX` and `mkstemp()` unless an external spool file has already been created by smbd. In-memory state is limited to stack/talloc contexts and backend interface selection; job mappings to RAP IDs are delegated to `rap_jobid.c`.

## Dependencies and Integration Points

This file depends on Samba loadparm (`lp_*`) configuration, TDB utility APIs, print interface tables, spoolss NDR for devmode serialization, printer notifications, pcap/printer-list state, server messaging, auth/session info, NT printing initialization, statvfs disk checks, and the background queue daemon helpers from `queue_process.h`. It integrates with `printspoolss.c` through job lifecycle functions, with registry/NT printing through `nt_printing_init()`, with backend-specific `struct printif` operations, and with smbd file close paths.

## Risks and Edge Cases

- Queue refresh is race-sensitive; `CACHE`, `MSG_PENDING`, `LOCK`, and `UPDATING` records reduce duplicate or overlapping lpq scans but stale PIDs or clock changes are explicitly handled.
- `sysjob_to_jobid()` traverses all printer DBs and is intentionally expensive.
- TDB record format is tightly coupled to `tdb_pack` formats and unguarded struct sizes for `print_status_struct`.
- `get_stored_queue_info()` mixes cached linear queue data with `jobs_added` and `jobs_changed`; corrupt list lengths are partly guarded by modulo checks.
- Job ID allocation retries only three candidate IDs and can report no spool space if collisions persist.
- Some status transitions are optimistic because backend delete/pause/resume commands may not synchronously prove final spooler state.
- External spool-file acceptance only verifies it is under the printer path and already exists; path boundary logic is security-relevant.

## Test Signals

The strongest local test signal is exercising Samba print tests with the virtual lp helper `printing/tests/vlp.c`, plus integration tests that start a job, write data, end it, query queue status, pause/resume/delete, and force background queue refresh. Targeted regression checks should include corrupt TDB list lengths, stale updater PID cleanup, clock-skew cache expiry, zero-length print cancellation, max-jobs enforcement, notification PID refcounts, and CUPS/generic backend selection.
