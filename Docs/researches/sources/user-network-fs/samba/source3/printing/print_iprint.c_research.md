# sources/user-network-fs/samba/source3/printing/print_iprint.c

Purpose: implements the Novell iPrint backend using libcups IPP primitives and Novell-specific operations/URIs. It supports printer discovery, job submit/delete/pause/resume, and queue enumeration; queue pause/resume are unsupported without credentials.

Important APIs and functions: `iprint_cache_reload()` sends `OPERATION_NOVELL_LIST_PRINTERS`, then `iprint_cache_add_printer()` queries each returned printer URI and filters out secure or SMB-disabled printers. `iprint_get_server_version()` detects NetWare/Linux server version and affects job time interpretation. `iprint_job_submit()` sends `IPP_PRINT_JOB`, unlinks the spool file on success, and records `job-id`. `iprint_queue_get()` fetches printer status, detects OES SP1 Unix-time behavior, gets jobs, and maps IPP job state into Samba queue entries. Job delete/pause/resume issue IPP operations against `/ipp/<printer>`.

Control flow: all operations connect to `lp_iprint_server()` or `cupsServer()` without encryption and with no password callback. Discovery is synchronous: a successful reload returns a transient `pcap_cache` for `pcap.c` to persist. Queue enumeration first fetches printer attributes, then job attributes.

State and persistence: stores no printer list itself; discovery results become `printer_list.tdb` through the pcap layer. Job operations mutate backend iPrint state and may set `pjob->sysjob`.

Dependencies and integration: depends on libcups, Samba loadparm, shared pcap helpers, printing structs, and the `iprint_printif` vtable. It is compiled only with `HAVE_IPRINT`.

Risks: uses fixed-size URI buffers and older string-copy patterns. Several fields are not UTF-8 converted unlike the CUPS backend. Authentication-required printers are silently ignored during discovery. Server-version time heuristics can misdate jobs if server clocks or version parsing are wrong. Tests should cover secure/SMB-disabled filtering, auth failures, NetWare versus OES SP1 time handling, job-id extraction, unsupported queue pause/resume, and malformed printer URIs.
