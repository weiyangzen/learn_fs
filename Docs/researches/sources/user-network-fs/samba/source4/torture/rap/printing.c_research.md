# sources/user-network-fs/samba/source4/torture/rap/printing.c

Purpose: This file builds the RAP printing torture sub-suite. It exercises raw SMB print job creation and RAP print queue, print job, and print destination calls across supported info levels.

Important APIs, types, and functions: `print_printjob()` creates a print job by opening `TORTURE_PRINT_FILE`, writing a small test page, and closing it. Test functions cover `rap_NetPrintQEnum`, `rap_NetPrintQGetInfo`, queue pause/resume, job pause/continue/delete, job enum/getinfo/setinfo, destination enum/getinfo, and the end-to-end `test_rap_print()`. `torture_rap_printing()` registers the `printing` suite.

Control flow: Queue enumeration loops over levels 0 through 5. Queue getinfo first checks that an empty queue name with a zero buffer returns `WERR_INVALID_PARAMETER`, then enumerates level 5 queues and queries each queue at levels 0 through 5. Job helpers enumerate queues, then enumerate or mutate jobs at levels 0 through 2. `test_rap_print()` pauses each queue, opens a second tree connection to that print share, submits a print job, enumerates jobs, validates getinfo, deletes each job, and resumes the queue.

State and persistence behavior: These tests intentionally mutate server print state: they create print jobs, pause/resume queues, set job comments, and delete jobs. Cleanup is mostly explicit via job deletion and queue resume, but interruption could leave queues paused or jobs present.

Dependencies and integration points: The file depends on SMB raw open/write/close APIs, RAP client calls, `torture_second_tcon()`, print share configuration, and `torture_suite_add_1smb_test()`. It is included by the broader RAP suite from `rap.c`.

Risks: It assumes a configured RAP-capable print environment and sufficient privileges to pause queues and delete jobs. Hard-coded job id `400` in `test_netprintjob()` may be server-dependent. Some tests assert transport success but do not always assert RAP status for every job operation.

Test signals: Passing tests show that RAP print queue discovery, per-level marshalling, job lifecycle operations, raw print submission, queue pause/resume, and print destination queries are interoperable with the target server.
