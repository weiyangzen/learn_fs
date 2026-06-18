# sources/user-network-fs/samba/source3/printing/print_cups.c

Purpose: implements the CUPS printing backend and CUPS printer discovery for Samba. It uses IPP over libcups for printer lists, job submission, queue enumeration, job control, and queue pause/resume.

Important APIs and functions: `cups_cache_reload()` starts asynchronous printer discovery. `cups_pcap_load_async()` forks a child, `cups_cache_reload_async()` queries `CUPS_GET_PRINTERS` and `CUPS_GET_CLASSES`, serializes `pcap_data`, and `cups_async_callback()` receives the blob, builds a `pcap_cache`, and persists it through `pcap_cache_replace()`. `cups_job_submit()` sends `IPP_PRINT_JOB` via `cupsDoFileRequest()` and records returned `job-id`. `cups_queue_get()` requests `IPP_GET_JOBS` and `IPP_GET_PRINTER_ATTRIBUTES` and maps IPP states into Samba `print_queue_struct` and `print_status_struct`. Job delete/pause/resume and queue pause/resume issue the corresponding IPP operations.

Control flow: most operations connect using `cups_connect()`, which honors `cups server`, encryption, and connection timeout settings. Requests add charset/language, URIs assembled with libcups, user/job attributes converted to UTF-8, then inspect response status. Discovery is asynchronous to avoid blocking the parent process; CUPS owns the post-cache-fill callback path.

State and persistence: no long-lived printer list is kept here. Discovery results flow through a pipe and are persisted in `printer_list.tdb` by `pcap_cache_replace()`. Job submission may unlink the spool file on success and updates `pjob->sysjob`.

Dependencies and integration: depends on libcups/IPP, tevent, Samba messaging/fork reinit, generated `ndr_printcap`, UTF-8 conversion, loadparm, and the `struct printif cups_printif` vtable.

Risks: async child/pipe handling is failure-prone; `cache_fd_event` prevents overlapping refreshes. URI assembly, encoding conversion, and response parsing must handle malformed CUPS data. Queue get returns partially allocated queues on some error paths. Tests should cover CUPS version compatibility macros, timeout behavior, async success/failure, class and printer discovery, IPP conflict statuses, file unlink on submit success only, queue state mapping, and no-password callback behavior.
